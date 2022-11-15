from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from rest_framework import pagination
from rest_framework import viewsets

from kolibri.core.auth.api import KolibriAuthPermissions
from kolibri.core.auth.api import KolibriAuthPermissionsFilter
from kolibri.core.auth.constants.collection_kinds import ADHOCLEARNERSGROUP
from kolibri.core.exams import models
from kolibri.core.exams import serializers
from kolibri.core.query import annotate_array_aggregate



class OptionalPageNumberPagination(pagination.PageNumberPagination):
    """
    Pagination class that allows for page number-style pagination, when requested.
    To activate, the `page_size` argument must be set. For example, to request the first 20 records:
    `?page_size=20&page=1`
    """
    page_size = None
    page_size_query_param = "page_size"


class ExamFilter(FilterSet):

    class Meta:
        model = models.Exam
        fields = ['collection', ]


def _ensure_raw_dict(d):
    if hasattr(d, "dict"):
        d = d.dict()
    return dict(d)


class ExamPermissions(KolibriAuthPermissions):
    # Overrides the default validator to sanitize the Exam POST Payload
    # before validation
    def validator(self, request, view, datum):
        model = view.get_serializer_class().Meta.model
        validated_data = view.get_serializer().to_internal_value(_ensure_raw_dict(datum))
        # Cannot have create assignments without creating the Exam first,
        # so this doesn't try to validate the Exam with a non-empty assignments list
        validated_data.pop('assignments')
        return request.user.can_create(model, validated_data)


class ExamViewset(viewsets.ModelViewSet):
    serializer_class = serializers.ExamSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = (ExamPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filter_class = ExamFilter

    def get_queryset(self):
        return models.Exam.objects.all()

    def consolidate(self, items, queryset):
        if items:
            exam_ids = [e["id"] for e in items]
            adhoc_assignments = models.ExamAssignment.objects.filter(
                exam_id__in=exam_ids, collection__kind=ADHOCLEARNERSGROUP
            )
            adhoc_assignments = annotate_array_aggregate(
                adhoc_assignments, learner_ids="collection__membership__user_id"
            )
            adhoc_assignments = {
                a["exam"]: a
                for a in adhoc_assignments.values("collection", "exam", "learner_ids")
            }
            for item in items:
                if item["id"] in adhoc_assignments:
                    adhoc_assignment = adhoc_assignments[item["id"]]
                    item["learner_ids"] = adhoc_assignments[item["id"]]["learner_ids"]
                    item["assignments"] = [
                        i
                        for i in item["assignments"]
                        if i != adhoc_assignment["collection"]
                    ]
                else:
                    item["learner_ids"] = []

        return items


    def perform_update(self, serializer):
        was_active = serializer.instance.active
        serializer.save()
        if was_active and not serializer.instance.active:
            # Has changed from active to not active, set completion_timestamps on all non closed examlogs
            serializer.instance.examlogs.filter(completion_timestamp__isnull=True).update(completion_timestamp=now())


class ExamAssignmentViewset(viewsets.ModelViewSet):
    pagination_class = OptionalPageNumberPagination
    permission_classes = (KolibriAuthPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter,)

    def get_queryset(self):
        return models.ExamAssignment.objects.all()

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'create':
            return serializers.ExamAssignmentCreationSerializer
        return serializers.ExamAssignmentRetrieveSerializer
