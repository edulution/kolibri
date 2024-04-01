import json
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from rest_framework import pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from kolibri.core.assessment.serializers import AssessmentSerializer, CreateAssessmentGroupSerializer,\
    CreateAssessmentSerializer, GetExamAssessmentSerializer, GroupAssessmentSerializer, GetGroupExamAssessmentSerializer
from rest_framework import status
from kolibri.core.api import ValuesViewset
from kolibri.core.auth.api import KolibriAuthPermissions
from kolibri.core.auth.api import KolibriAuthPermissionsFilter
from kolibri.core.auth.constants.collection_kinds import ADHOCLEARNERSGROUP
from kolibri.core.content.models import ContentNode
from kolibri.core.content.utils.annotation import total_file_size
from kolibri.core.assessment import models
from kolibri.core.assessment import serializers
from kolibri.core.logger.models import MasteryLog
from kolibri.core.query import annotate_array_aggregate
from .serializers import ExamAssessmentSerializer


class OptionalPageNumberPagination(pagination.PageNumberPagination):
    """
    Pagination class that allows for page number-style pagination, when requested.
    To activate, the `page_size` argument must be set. For example, to request the first 20 records:
    `?page_size=20&page=1`
    """

    page_size = None
    page_size_query_param = "page_size"


class ExamAssessmentFilter(FilterSet):
    class Meta:
        model = models.ExamAssessment
        fields = ["collection"]


def _ensure_raw_dict(d):
    if hasattr(d, "dict"):
        d = d.dict()
    return dict(d)


class ExamAssessmentPermissions(KolibriAuthPermissions):
    # Overrides the default validator to sanitize the Exam POST Payload
    # before validation
    def validator(self, request, view, datum):
        model = view.get_serializer_class().Meta.model
        validated_data = view.get_serializer().to_internal_value(
            _ensure_raw_dict(datum)
        )
        # Cannot have create assignments without creating the Exam first,
        # so this doesn't try to validate the Exam with a non-empty assignments list
        validated_data.pop("assignments", [])
        validated_data.pop("learner_ids", [])
        return request.user.can_create(model, validated_data)


class AssessmentViewset(ValuesViewset):
    serializer_class = serializers.ExamAssessmentSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = (ExamAssessmentPermissions,)
    filter_backends = (KolibriAuthPermissionsFilter, DjangoFilterBackend)
    filter_class = ExamAssessmentFilter

    values = (
        "id",
        "title",
        "question_count",
        "question_sources",
        "seed",
        "active",
        "collection",
        "archive",
        "date_archived",
        "date_activated",
        "assignment_collections",
        "creator",
        "data_model_version",
        "learners_see_fixed_order",
    )

    field_map = {"assignmentassessments": "assignment_collections"}

    def get_queryset(self):
        return models.ExamAssessment.objects.all()

    def annotate_queryset(self, queryset):
        return annotate_array_aggregate(
            queryset, assignment_collections="assignmentassessments__collection"
        )

    def consolidate(self, items, queryset):
        if items:
            exam_ids = [e["id"] for e in items]
            adhoc_assignments = models.ExamAssignmentAssessment.objects.filter(
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
                    item["assignmentassessments"] = [
                        i
                        for i in item["assignmentassessments"]
                        if i != adhoc_assignment["collection"]
                    ]
                else:
                    item["learner_ids"] = []

        return items

    def perform_update(self, serializer):
        was_active = serializer.instance.active
        was_archived = serializer.instance.archive
        serializer.save()

        masterylog_queryset = MasteryLog.objects.filter(
            summarylog__content_id=serializer.instance.id
        )

        if was_active and not serializer.instance.active:
            # Has changed from active to not active, set completion_timestamps on all non complete masterylogs
            masterylog_queryset.filter(completion_timestamp__isnull=True).update(
                completion_timestamp=now()
            )

        if not was_archived and serializer.instance.archive:
            # It was not archived (closed), but now it is - so we set all MasteryLogs as complete
            masterylog_queryset.update(complete=True)

    @action(detail=False)
    def size(self, request, **kwargs):
        exams = self.filter_queryset(self.get_queryset())
        exams_sizes_set = []
        for exam in exams:
            quiz_size = {}
            quiz_nodes = ContentNode.objects.filter(
                id__in={source["exercise_id"] for source in exam.question_sources}
            )
            quiz_size[exam.id] = total_file_size(quiz_nodes)
            exams_sizes_set.append(quiz_size)

        return Response(exams_sizes_set)
    

class GroupAssessmentViewset(ViewSet):
    queryset = models.ExamAssessmentGroup.objects.all()
    serializer_class = AssessmentSerializer

    def retrieve(self, request, pk=None):
        try:
            assessment = self.queryset.filter(collection_id=pk)
            serializer = self.serializer_class(assessment, many=True)
            return Response(serializer.data)
        except models.ExamAssessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class CreateAssessmentRecord(ViewSet):
    def create(self, request, pk=None):
        from .models import ExamAssessment

        try:

            request_data = request.data

            assessment = request_data.get('assessments')

            collection = request_data.get('collection')
            date_activated = request_data.get('date_activated')
            date_archived = request_data.get('date_archived')
            learner_id = request_data.get('learner_id')
            title = request_data.get('title')
            channel_id = request_data.get('channel_id')
            creator_id = request.user.id
            if not creator_id:
                creator_id = request_data.get('creator_id')
            # test_data = ExamAssessmentGroup.objects.create(collection_id = collection, date_activated=date_activated, date_archived=date_archived, learner_id=learner_id, title=title, creator_id='ab8e752daeefb1fade99bf34efcafe6e')
            
            id_available = models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)

            if not id_available:

                field_update = {'date_activated': date_activated, 'date_archived':date_archived, 'learner_id':learner_id,'title':title, 'collection':collection, 'creator': creator_id, 'channel_id': channel_id}
                
                group_serializer = CreateAssessmentGroupSerializer(data=field_update)

                group_serializer.is_valid(raise_exception=True)
                
                group_serializer.save()

            fetch_id = models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)
            
            obj = None
            if fetch_id.exists():
                obj = fetch_id[0] 
            
            is_available = models.ExamAssessment.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)

            if not is_available:
            
                for test in assessment:
                    
                    question_source = test.get('question_sources')
                    question_count = test.get('question_count')
                    new_title = test.get('title')

                    insert_record = ExamAssessment.objects.create(collection_id = collection, date_activated=date_activated, date_archived=date_archived, learner_id=learner_id, title=new_title, question_sources = question_source, question_count = question_count , assessment_group_id = obj.id, channel_id = channel_id,  creator_id=creator_id)

                # asess_dict = {'date_activated': date_activated, 'date_archived':date_archived, 'learner_id':learner_id,'title':new_title, 'collection':collection,'question_sources':str(question_source), 'question_count':question_count}
                # assessment_serializer = CreateAssessmentSerializer(data = asess_dict)
                # assessment_serializer.is_valid(raise_exception=True)
                # assessment_serializer.save(creator_id= 'ab8e752daeefb1fade99bf34efcafe6e')
                    
                assessment_record = models.ExamAssessment.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)
                instance_list = []
                final_response_list = []
        
                for instance in assessment_record:
                    assessment_dict = {'id':instance.id, 'title':instance.title}
                    final_dict = {'id':instance.id, 'title':instance.title,'question_count': instance.question_count, 'question_sources': instance.question_sources,'seed':instance.seed, 'learners_see_fixed_order': instance.learners_see_fixed_order, 'date_activated':instance.date_activated}
                    instance_list.append(assessment_dict)
                    final_response_list.append(final_dict)

                if len(instance_list) != 0: 
                    to_dict = {'assessment_map': json.dumps(instance_list), 'current_assessment_id': instance_list[0]['id']}
                    # assessement_serializer = CreateAssessmentGroupSerializer(data=to_dict)
                    # assessement_serializer.is_valid(raise_exception=True)
                    # assessement_serializer.save()

                    updated_count = models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection).update(**to_dict)

                return Response(final_response_list, status=status.HTTP_200_OK)
            
            return Response({"error": "Assessment for this learner already exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except models.ExamAssessmentGroup.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        

# class ExamAssessmentStartViewSet(ViewSet):
#    def update(self, request, pk=None):  # Ensure pk is included in the method signature
#         try:
#             # Fetch the instances based on the assessment_group_id
#             update_dict = {'active': 1}
#             available_id = models.ExamAssessment.objects.filter(assessment_group_id=pk)
            
#             if available_id:
#                 assessment_instance_count = models.ExamAssessment.objects.filter(assessment_group_id=pk).update(**update_dict)
#             else:
#                 return Response({'message': 'Invalid Assessment ID'})
#             # Fetch the instance based on the primary key

#             available_group_id = models.ExamAssessmentGroup.objects.filter(id=pk)
#             if available_group_id:
#                 group_assessment_instance_count = models.ExamAssessmentGroup.objects.filter(id=pk).update(**update_dict)
#             else:
#                 return Response({'message': 'Invalid Group ID'})

#             # Optionally, you can return a success response indicating the update was successful
#             return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
#         except models.ExamAssessmentGroup.DoesNotExist:
#             # Handle case where no instance with the given pk is found
            # return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        
class ExamAssessmentStartViewSet(ViewSet):
   def partial_update(self, request, pk=None):  # Ensure pk is included in the method signature
        try:
            # Fetch the instances based on the assessment_group_id
            update_dict = {'active': 1}
            available_id = models.ExamAssessment.objects.filter(assessment_group_id=pk)
            
            if available_id:
                assessment_instance_count = models.ExamAssessment.objects.filter(assessment_group_id=pk).update(**update_dict)
            else:
                return Response({'message': 'Invalid Assessment ID'})
            # Fetch the instance based on the primary key

            available_group_id = models.ExamAssessmentGroup.objects.filter(id=pk)
            if available_group_id:
                group_assessment_instance_count = models.ExamAssessmentGroup.objects.filter(id=pk).update(**update_dict)
            else:
                return Response({'message': 'Invalid Group ID'})

            # Optionally, you can return a success response indicating the update was successful
            return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
        except models.ExamAssessmentGroup.DoesNotExist:
            # Handle case where no instance with the given pk is found
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        

# class ExamAssessmentStopViewSet(ViewSet):
#    def update(self, request, pk=None):  # Ensure pk is included in the method signature
#         try:
#             # Fetch the instances based on the assessment_group_id
#             update_dict = {'archive': 1}
#             available_id = models.ExamAssessment.objects.filter(assessment_group_id=pk)
            
#             if available_id:
#                 assessment_instance_count = models.ExamAssessment.objects.filter(assessment_group_id=pk).update(**update_dict)
#             else:
#                 return Response({'message': 'Invalid Assessment ID'})
#             # Fetch the instance based on the primary key

#             available_group_id = models.ExamAssessmentGroup.objects.filter(id=pk)
#             if available_group_id:
#                 group_assessment_instance_count = models.ExamAssessmentGroup.objects.filter(id=pk).update(**update_dict)
#             else:
#                 return Response({'message': 'Invalid Group ID'})

#             # Optionally, you can return a success response indicating the update was successful
#             return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
#         except models.ExamAssessmentGroup.DoesNotExist:
#             # Handle case where no instance with the given pk is found
#             return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
class ExamAssessmentStopViewSet(ViewSet):
    def partial_update(self, request, pk=None):
        try:
            update_dict = {'archive': 1}
            available_id = models.ExamAssessment.objects.filter(assessment_group_id=pk)
            if available_id:
                assessment_instance_count = models.ExamAssessment.objects.filter(assessment_group_id=pk).update(**update_dict)
            else:
                return Response({'message': 'Invalid Assessment ID'}, status=status.HTTP_404_NOT_FOUND)

            available_group_id = models.ExamAssessmentGroup.objects.filter(id=pk)
            if available_group_id:
                group_assessment_instance_count = models.ExamAssessmentGroup.objects.filter(id=pk).update(**update_dict)
            else:
                return Response({'message': 'Invalid Group ID'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
        except models.ExamAssessmentGroup.DoesNotExist:
            # Handle case where no instance with the given pk is found
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        

class GetLearnerAssessmentViewset(ViewSet):
    queryset = models.ExamAssessmentGroup.objects.all()
    serializer_class = GetGroupExamAssessmentSerializer

    def list(self, request):
        try:
            learner_id = request.query_params.get('learner_id')
            classroom_id = request.query_params.get('classroom_id')

            if not learner_id:
                return Response({"error": "Learner ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            learner_assessments = self.queryset.filter(learner_id=learner_id, collection=classroom_id, active=True)
            serializer = self.serializer_class(learner_assessments, many=True)

            # Fetch question sources based on current_assessment
            assessment_ids = [assessment['current_assessment'] for assessment in serializer.data]
            question_sources = models.ExamAssessment.objects.filter(id__in=assessment_ids).values_list('question_sources', flat=True)

            return Response(serializer.data)
        except models.ExamAssessment.DoesNotExist:
            return Response({"error": "Learner Assessments not found"}, status=status.HTTP_404_NOT_FOUND)


class FetchAssessmentGroupData(ViewSet):
    queryset = models.ExamAssessmentGroup.objects.all()
    serializer_class = GroupAssessmentSerializer

    def retrieve(self, request, pk=None):
        try:
            assessment_group = self.queryset.get(id=pk)
            serializer = self.serializer_class(assessment_group)

            # Fetch ExamAssessment details based on current_assessment_id
            current_assessment_id = assessment_group.current_assessment_id
            exam_assessment = models.ExamAssessment.objects.get(id=current_assessment_id)
            exam_assessment_serializer = ExamAssessmentSerializer(exam_assessment)

            # Construct response data
            response_data = {
                "id": current_assessment_id,
                "title": serializer.data['title'],
                "date_created": serializer.data['date_created'],
                "date_archived": serializer.data['date_archived'],
                "date_activated": serializer.data['date_activated'],
                "archive": serializer.data['archive'],
                "question_sources": exam_assessment_serializer.data['question_sources'],
                "data_model_version": exam_assessment_serializer.data['data_model_version'],
                "learners_see_fixed_order": exam_assessment_serializer.data['learners_see_fixed_order'],
                "seed": exam_assessment_serializer.data['seed'],
                "assignments": exam_assessment_serializer.data['assignments']
            }

            return Response(response_data)
        except models.ExamAssessmentGroup.DoesNotExist:
            return Response({"error": "Assessment Group not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.ExamAssessment.DoesNotExist:
            return Response({"error": "Exam Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

