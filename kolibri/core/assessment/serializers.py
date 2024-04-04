from rest_framework import serializers
from .models import ExamAssessmentGroup
from kolibri.core.assessment.models import ExamAssessment


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAssessmentGroup
        fields = (
            "id",
            "title",
            "active",
            "date_activated",
            'date_created',
            "date_archived",
            "collection",
            "archive",
            "learner_id",
        )

class CreateAssessmentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamAssessmentGroup
        fields = (
            "title",
            "date_activated",
            "date_archived",
            "collection",
            "archive",
            "learner_id",
            "creator",
            "assessment_map",
            "channel_id"
        )


class GetExamAssessmentSerializer(serializers.ModelSerializer):
    question_sources = serializers.JSONField()

    class Meta:
        model = ExamAssessment
        fields = (
            'question_sources',
            'title',
            'id',
        )

class GetGroupExamAssessmentSerializer(serializers.ModelSerializer):
    current_assessment = GetExamAssessmentSerializer()
    class Meta:
        model = ExamAssessmentGroup
        fields = (
            'id',
            'collection',
            'active',
            'archive',
            'title',
            'current_assessment',
        )


class ExamAssessmentSerializer(serializers.ModelSerializer):
    question_sources = serializers.JSONField()
    class Meta:
        model = ExamAssessment
        fields = (
            "id",
            "title",
            "question_sources",
            "data_model_version",
            "learners_see_fixed_order",
            "seed",
            "date_created",
            "date_archived",
            "date_activated",
            "archive",
            "active",
            "assignments",
        )

class ExamAssessmentGroupDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAssessment
        fields = (
            "id",
            "title"
        )

class GroupAssessmentSerializer(serializers.ModelSerializer):
    current_assessment = ExamAssessmentGroupDataSerializer()
    class Meta:
        model = ExamAssessmentGroup
        fields = (
            "id",
            "title",
            "date_created",
            "date_archived",
            "date_activated",
            "archive",
            "active",
            "current_assessment",
            "last_assessment",
            "learner_id",
            "collection"
        )


class MarkAssessmentSerializer(serializers.Serializer):
    learner_id = serializers.CharField()
    assessment_id = serializers.CharField()
    assessment_group_id = serializers.CharField()