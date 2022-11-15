from collections import OrderedDict

from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from kolibri.core import error_constants
from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import FacilityUser
from kolibri.core.exams.models import Exam
from kolibri.core.exams.models import ExamAssignment
from kolibri.core.auth.models import Membership
from kolibri.core.auth.constants.collection_kinds import ADHOCLEARNERSGROUP
from kolibri.core.auth.utils import create_adhoc_group_for_learners



class NestedCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = (
            'id', 'name', 'kind',
        )


class NestedExamAssignmentSerializer(serializers.ModelSerializer):

    collection = NestedCollectionSerializer(read_only=True)

    class Meta:
        model = ExamAssignment
        fields = (
            'id', 'exam', 'collection',
        )


class ExamAssignmentCreationSerializer(serializers.ModelSerializer):
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=False, queryset=FacilityUser.objects.all())
    collection = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Collection.objects.all())

    class Meta:
        model = ExamAssignment
        fields = (
            'id', 'exam', 'collection', 'assigned_by',
        )
        read_only_fields = ('assigned_by',)

    def to_internal_value(self, data):
        # Make a new OrderedDict from the input, which could be an immutable QueryDict
        data = OrderedDict(data)
        data['assigned_by'] = self.context['request'].user.id
        return super(ExamAssignmentCreationSerializer, self).to_internal_value(data)


class ExamAssignmentRetrieveSerializer(serializers.ModelSerializer):

    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)
    collection = NestedCollectionSerializer(read_only=True)
    collection_kind = SerializerMethodField()

    def get_collection_kind(self, instance):
        return instance.collection.kind

    class Meta:
        model = ExamAssignment
        fields = (
            'id', 'exam', 'collection', 'assigned_by', 'collection_kind',
        )
        read_only_fields = ('assigned_by', 'collection', 'collection_kind', )


class ExamAssignmentNestedSerializer(ExamAssignmentRetrieveSerializer):

    collection = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Collection.objects.all())

    class Meta(ExamAssignmentRetrieveSerializer.Meta):
        read_only_fields = ('assigned_by', 'collection_kind', 'exam', )


class ExamSerializer(serializers.ModelSerializer):

    assignments = ExamAssignmentNestedSerializer(many=True)
    question_sources = serializers.JSONField(default='[]')
    creator = serializers.PrimaryKeyRelatedField(read_only=False, queryset=FacilityUser.objects.all())

    class Meta:
        model = Exam
        fields = (
            'id', 'title', 'question_count', 'question_sources', 'seed',
            'active', 'collection', 'archive', 'assignments', 'creator', 'data_model_version',
            'learners_see_fixed_order'
        )
        read_only_fields = ('data_model_version',)

    def validate(self, attrs):
        title = attrs.get('title')
        # first condition is for creating object, second is for updating
        collection = attrs.get('collection') or getattr(self.instance, 'collection')
        # if obj doesn't exist, return data
        try:
            obj = Exam.objects.get(title__iexact=title, collection=collection)
        except Exam.DoesNotExist:
            return attrs
        # if we are updating object, and this `instance` is the same object, return data
        if self.instance and obj.id == self.instance.id:
            return attrs
        else:
            raise serializers.ValidationError('The fields title, collection must make a unique set.', code=error_constants.UNIQUE)

    def validate_question_sources(self, value):
        for question in value:
            if 'exercise_id' not in question:
                raise serializers.ValidationError("Question missing 'exercise_id'")
            if 'question_id' not in question:
                raise serializers.ValidationError("Question missing 'question_id'")
            if 'title' not in question:
                raise serializers.ValidationError("Question missing 'title'")
        return value

    def to_internal_value(self, data):
        # Make a new OrderedDict from the input, which could be an immutable QueryDict
        data = OrderedDict(data)
        if 'creator' not in data:
            if self.context['view'].action == 'create':
                data['creator'] = self.context['request'].user.id
            else:
                # Otherwise we are just updating the exam, so allow a partial update
                self.partial = True
        return super(ExamSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        assignees = validated_data.pop('assignments')
        validated_data['data_model_version'] = 1
        new_exam = Exam.objects.create(**validated_data)
        # Create all of the new ExamAssignment
        for assignee in assignees:
            self._create_exam_assignment(
                exam=new_exam,
                collection=assignee['collection']
            )
        return new_exam

    def _create_exam_assignment(self, **params):
        return ExamAssignment.objects.create(
            assigned_by=self.context['request'].user,
            **params
        )

    def update(self, instance, validated_data):
        # Update the scalar fields
        instance.title = validated_data.get('title', instance.title)
        instance.active = validated_data.get('active', instance.active)

        # Add/delete any new/removed Assignments
        if 'assignments' in validated_data:
            assignees = validated_data.pop('assignments')
            current_group_ids = set(instance.assignments.values_list('collection__id', flat=True))
            new_group_ids = set(x['collection'].id for x in assignees)

            for id in new_group_ids - current_group_ids:
                self._create_exam_assignment(
                    exam=instance,
                    collection=Collection.objects.get(id=id)
                )

            ExamAssignment.objects.filter(
                exam_id=instance.id,
                collection_id__in=(current_group_ids - new_group_ids)
            ).delete()

        instance.save()
        return instance

    def _update_learner_ids(self, instance, learners):
        try:
            adhoc_group_assignment = ExamAssignment.objects.select_related(
                "collection"
            ).get(exam=instance, collection__kind=ADHOCLEARNERSGROUP)
        except ExamAssignment.DoesNotExist:
            adhoc_group_assignment = None
        if not learners:
            # Setting learner_ids to empty, so only need to do something
            # if there is already an adhoc_group_assignment defined
            if adhoc_group_assignment is not None:
                # Adhoc group already exists delete it and the assignment
                # cascade deletion should also delete the adhoc_group_assignment
                adhoc_group_assignment.collection.delete()
        else:
            if adhoc_group_assignment is None:
                # There is no adhoc group right now, so just make a new one
                adhoc_group = create_adhoc_group_for_learners(
                    instance.collection, learners
                )
                self._create_exam_assignment(exam=instance, collection=adhoc_group)
            else:
                # There is an adhoc group, so we need to potentially update its membership
                original_learner_ids = Membership.objects.filter(
                    collection=adhoc_group_assignment.collection
                ).values_list("user_id", flat=True)
                original_learner_ids_set = set(original_learner_ids)
                learner_ids_set = set(learner.id for learner in learners)
                if original_learner_ids_set != learner_ids_set:
                    # Only bother to do anything if these are different
                    new_learner_ids = learner_ids_set - original_learner_ids_set
                    deleted_learner_ids = original_learner_ids_set - learner_ids_set

                    if deleted_learner_ids:
                        Membership.objects.filter(
                            collection=adhoc_group_assignment.collection,
                            user_id__in=deleted_learner_ids,
                        ).delete()

                    for new_learner_id in new_learner_ids:
                        Membership.objects.create(
                            user_id=new_learner_id,
                            collection=adhoc_group_assignment.collection,
                        )