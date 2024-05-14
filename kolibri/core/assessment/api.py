import json
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework import FilterSet
from kolibri.plugins.edulutionCoach.class_summary_api import serialize_coach_assigned_assessment_status, to_fetch_learner_status
from rest_framework import pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from kolibri.core.assessment.serializers import AssessmentSerializer, CreateAssessmentGroupSerializer,GroupAssessmentSerializer, GetGroupExamAssessmentSerializer
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
from .serializers import MarkAssessmentSerializer, StartRestartTest
from datetime import datetime
from kolibri.core.logger.models import AttemptLog,ContentSessionLog,MasteryLog,ContentSummaryLog
import random
import pandas as pd
from .z_assessments_constant import AssessmentConstant

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
        "current_question_count",
        "current_question_sources",
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
        from .models import ExamAssessment, ExamAssignmentAssessment, AssessmentConfig

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

            assessment_map_obj = AssessmentConfig.objects.get(channel_id=channel_id)

            if not assessment_map_obj:
                return Response({"error": "Assessment map config not found"}, status=status.HTTP_404_NOT_FOUND)
            
            assessment_group_obj = models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id=collection)

            assessment_map_df = pd.DataFrame(assessment_map_obj.assessment_map)
            assessment_map_df[(assessment_map_df['type'] == AssessmentConstant.PRE_TEST) & (assessment_map_df['order'] == AssessmentConstant.ORDER) & (assessment_map_df['level'] == AssessmentConstant.LEVEL)].reset_index(drop=True)
            
            if not assessment_group_obj:

                field_update = {
                    'date_activated': date_activated,
                    'date_archived':date_archived,
                    'learner_id':learner_id,
                    'title':title,
                    'collection':collection,
                    'creator': creator_id,
                    'channel_id': channel_id
                }
                
                group_serializer = CreateAssessmentGroupSerializer(data=field_update)

                group_serializer.is_valid(raise_exception=True)
                
                group_serializer.save()

                assessment_group_obj = models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)
            
            object = None
            if assessment_group_obj.exists():
                object = assessment_group_obj[0]
            
            is_available = models.ExamAssessment.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection)

            instance_list = []
            final_response_list = []

            if not is_available:
                for test in assessment_map_obj.assessment_map:
                    map_object = next((d for d in assessment if d['content_id'] == test['id']), None)
                    if map_object:
                        question_source = map_object.get('question_sources')
                        question_count = map_object.get('question_count')
                        new_title = map_object.get('title')
                        current_question_limit = map_object.get('limit')
                        assessment_topic = map_object.get('exercises')

                        current_question_source = []

                        exercise_questions = {topic['id']: [] for topic in assessment_topic}
                        for source in question_source:
                            exercise_id = source['exercise_id']
                            exercise_questions[exercise_id].append(source)
                        
                        current_question_count = AssessmentConstant.DEFAULT
                        for topic in assessment_topic:
                            exercise_id = topic['id']
                            weightage = topic['weightage']
                            current_question_count += weightage
                            matched_question_ids = exercise_questions.get(exercise_id, [])
                            random_questions = random.sample(matched_question_ids, min(weightage, len(matched_question_ids)))
                            current_question_source.append(random_questions)
        
                        current_question_source_list = [item for sublist in current_question_source for item in sublist]

                        instance = ExamAssessment.objects.create(
                            collection_id = collection,
                            date_activated=date_activated,
                            date_archived=date_archived,
                            learner_id=learner_id,
                            title=new_title,
                            question_sources = question_source,
                            question_count = question_count ,
                            assessment_group_id = object.id,
                            channel_id = channel_id, 
                            creator_id=creator_id,
                            current_questions_limit=current_question_limit,
                            current_question_sources = current_question_source_list,
                            current_question_count = current_question_count,
                            topicwise_weightage = assessment_topic,
                            extra_data = {'type': test['type'], 'level': test['level']}
                        )

                        ExamAssignmentAssessment.objects.create(collection_id = collection, exam_id=instance.id, assigned_by_id=creator_id)

                        final_dict = {
                            'id':instance.id,
                            'title':new_title,
                            'question_count': question_count,
                            'question_sources': question_source,
                            'seed': AssessmentConstant.DEFAULT,
                            'learners_see_fixed_order': AssessmentConstant.DEFAULT,
                            'date_activated': date_activated
                        }

                        instance_list.append({
                            **test,
                            'id': instance.id,
                            'content_id': test['id'],
                        })
                        final_response_list.append(final_dict)

                if len(instance_list) != AssessmentConstant.DEFAULT: 
                    to_dict = {'assessment_map': json.dumps(instance_list), 'current_assessment_id': instance_list[0]['id'], 'current_assessment_level': instance_list[0]['level'], 'current_assessment_type': instance_list[0]['type']}
                    models.ExamAssessmentGroup.objects.filter(learner_id=learner_id, channel_id=channel_id, collection_id = collection).update(**to_dict)

                return Response(final_response_list, status=status.HTTP_200_OK)
            
            return Response({"error": "Assessment for this learner already exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except models.ExamAssessmentGroup.DoesNotExist:
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)

class ExamAssessmentStartViewSet(ViewSet):
   def partial_update(self, request, pk=None):  # Ensure pk is included in the method signature
        try:
            # Fetch the instances based on the assessment_group_id
            update_dict = {'active': AssessmentConstant.ACTIVE}
            
            available_id = models.ExamAssessment.objects.filter(assessment_group_id=pk)

            available_group_id = models.ExamAssessmentGroup.objects.get(id=pk)
            
            assessment_map = available_group_id.assessment_map

            first_assessment_map = assessment_map[0]['id']

            if available_id:
                assessment_instance = models.ExamAssessment.objects.get(id=first_assessment_map)
                assessment_instance.previous_question_sources = assessment_instance.current_question_sources
                assessment_instance.__dict__.update({**update_dict, 'attempt_count': AssessmentConstant.ATTEMPT_COUNT})
                assessment_instance.save()
            else:
                return Response({'message': 'Invalid Assessment ID'})
            # Fetch the instance based on the primary key

            if available_group_id:
                group_assessment_instance_count = models.ExamAssessmentGroup.objects.filter(id=pk).update(**update_dict)
            else:
                return Response({'message': 'Invalid Group ID'})

            # Optionally, you can return a success response indicating the update was successful
            return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
        except models.ExamAssessmentGroup.DoesNotExist:
            # Handle case where no instance with the given pk is found
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)
        

class AssessmentTestViewSet(ViewSet):
   serializer_class = StartRestartTest
   def create(self, request): 
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                assessment_id = serializer.validated_data.get('assessment_id')
                flag = serializer.validated_data.get('flag')

                assessment_obj = models.ExamAssessment.objects.get(id = assessment_id)
    
                if assessment_obj:
                    update_dict = {}
                    
                    if flag == AssessmentConstant.START or flag == AssessmentConstant.RESTART:
                        update_dict = {
                            'active': AssessmentConstant.ACTIVE,
                            'attempt_count': assessment_obj.attempt_count + 1
                        }

                        assessment_obj.previous_question_sources = assessment_obj.current_question_sources

                        if assessment_obj.attempt_count >= AssessmentConstant.LEVEL_AND_COUNT:

                            # assessment_obj.previous_question_sources = assessment_obj.current_question_sources
                            current_question_source = []

                            exercise_questions = {topic['id']: [] for topic in assessment_obj.topicwise_weightage}

                            # Populate exercise_questions dictionary with question sources
                            for source in assessment_obj.question_sources:
                                exercise_id = source['exercise_id']
                                exercise_questions[exercise_id].append(source)

                            # Loop through each topic and select random questions
                            for topic in assessment_obj.topicwise_weightage:
                                exercise_id = topic['id']
                                weightage = topic['weightage']
                                matched_question_ids = exercise_questions.get(exercise_id, [])
                                random_questions = random.sample(matched_question_ids, min(weightage, len(matched_question_ids)))
                                current_question_source.extend(random_questions)

                            assessment_obj.current_question_sources = current_question_source
                            assessment_obj.previous_question_sources = current_question_source

                    elif flag == AssessmentConstant.STOP:
                        update_dict = {
                            'active': AssessmentConstant.STOP
                        }

                    assessment_obj.__dict__.update(**update_dict)
                    assessment_obj.save()
                    return Response({'message': 'Instances updated successfully'}, status=status.HTTP_200_OK)
                
                else:
                    return Response({'message': 'Invalid Assessment ID'})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)       
        
        except models.ExamAssessment.DoesNotExist:
            # Handle case where no instance with the given pk is found
            return Response({"error": "Instance not found"}, status=status.HTTP_404_NOT_FOUND)

class ExamAssessmentStopViewSet(ViewSet):
    def partial_update(self, request, pk=None):
        try:
            update_dict = {'archive': AssessmentConstant.ARCHIVE}
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

def find_index(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

class FetchAssessmentGroupData(ViewSet):
    queryset = models.ExamAssessmentGroup.objects.all()
    serializer_class = GroupAssessmentSerializer

    def retrieve(self, request, pk=None):
        try:
            assessment_group = self.queryset.get(id=pk)
            serializer = self.serializer_class(assessment_group)

            exam_assessments = models.ExamAssessment.objects.filter(assessment_group=pk)
            exam_assessments_list = []
            
            for assessment in exam_assessments:
                assessment_dict = {
                    "id": assessment.id,
                    "title": assessment.title,
                    "question_sources": assessment.question_sources,
                    "data_model_version": assessment.data_model_version,
                    "learners_see_fixed_order": assessment.learners_see_fixed_order,
                    "seed": assessment.seed,
                    "date_created": assessment.date_created,
                    "date_archived": assessment.date_archived,
                    "date_activated": assessment.date_activated,
                    "archive": assessment.archive,
                    "active": assessment.active,
                    "assignments": assessment.assignments,
                    "exercises": [],
                    "extra_data": assessment.extra_data,
                    "attempt_count": assessment.attempt_count,
                }

                for question in assessment.question_sources:
                    exercise_id = question["exercise_id"]
                    
                    if find_index(assessment_dict["exercises"], "id", exercise_id) == -1:
                        exercise_title = ContentNode.objects.get(id=question["exercise_id"]).title
                        assessment_dict["exercises"].append({
                            "id": question["exercise_id"],
                            "title": exercise_title,
                        })
                    
                exam_assessments_list.append(assessment_dict)
            
            # Construct response data
            response_data = {
                "id": pk,
                "title": serializer.data['title'],
                "date_created": serializer.data['date_created'],
                "date_archived": serializer.data['date_archived'],
                "date_activated": serializer.data['date_activated'],
                "archive": serializer.data['archive'],
                "active": serializer.data['active'],
                "learner_id": serializer.data['learner_id'],
                "collection_id": serializer.data['collection'],
                "current_assessment_id": serializer.data['current_assessment'],
                "last_assessment_id": serializer.data['last_assessment'],
                "assessments": exam_assessments_list,
                "learner_status": to_fetch_learner_status(serializer.data['learner_id'], assessment_group_id=pk),
            }

            return Response(response_data)
        except models.ExamAssessmentGroup.DoesNotExist:
            return Response({"error": "Assessment Group not found"}, status=status.HTTP_404_NOT_FOUND)
        except models.ExamAssessment.DoesNotExist:
            return Response({"error": "Exam Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

class MarkAssessmentViewset(ViewSet):
    serializer_class = MarkAssessmentSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            assessment_id = serializer.validated_data.get('assessment_id')
            assessment_group_id = serializer.validated_data.get('assessment_group_id')

            try:
                assessment_group_level = models.ExamAssessmentGroup.objects.get(id=assessment_group_id)

                if not assessment_group_level:
                    return Response({"error": "Assessment group not found"}, status=status.HTTP_404_NOT_FOUND)
     
            except models.ExamAssessmentGroup.DoesNotExist:
                return Response({"error": "Assessment group not found"}, status=status.HTTP_404_NOT_FOUND)

            exam_assessments = models.ExamAssessment.objects.filter(assessment_group=assessment_group_id)
            assessment_level = models.ExamAssessment.objects.filter(id=assessment_id).last()

            question_count  = 1
            user_id = assessment_group_level.learner_id
            
            if assessment_level:
                question_count = assessment_level.question_count
                user_id = assessment_level.learner_id

            learner_status = serialize_coach_assigned_assessment_status(exam_assessments)

            num_correct_value = learner_status[0]['num_correct']

            if num_correct_value == None:
                num_correct_value = AssessmentConstant.DEFAULT

            percentage = (num_correct_value / question_count) * 100
            
            assessment_map = assessment_group_level.assessment_map
            current_assessment_id = assessment_group_level.current_assessment_id
            last_assessment_id = assessment_group_level.last_assessment_id

            current_id, last_id, archieve_flag  = self.process_assessment_list(assessment_map, current_assessment_id, last_assessment_id, percentage )
            
            assessment_map_df = pd.DataFrame(assessment_map)
           
            current_assessment = assessment_map_df[(assessment_map_df['id'] == current_id)].reset_index(drop = True)
            last_assessment = assessment_map_df[(assessment_map_df['id'] == last_id)].reset_index(drop = True)

            if archieve_flag == True:
                assessment_group_level.current_assessment_id = current_id
                assessment_group_level.current_assessment_type = current_assessment['type'][0]
                assessment_group_level.current_assessment_level = current_assessment['level'][0]
                assessment_group_level.last_assessment_id = last_id
                assessment_group_level.last_assessment_type = last_assessment['type'][0]
                assessment_group_level.last_assessment_level = last_assessment['level'][0]
                assessment_level.archive = True
                assessment_level.date_archived = datetime.now()
                assessment_group_level.archive = True
                assessment_group_level.date_archived = datetime.now()
            
            else:
                Individual_current_assessment_level = models.ExamAssessment.objects.filter(id=current_assessment['id'][0]).last() 
                Individual_last_assessment_level = models.ExamAssessment.objects.filter(id=last_assessment['id'][0]).last() 

                assessment_group_level.current_assessment_id = current_id
                assessment_group_level.current_assessment_type = current_assessment['type'][0]
                assessment_group_level.current_assessment_level = current_assessment['level'][0]
                assessment_group_level.last_assessment_id = last_id
                assessment_group_level.last_assessment_type = last_assessment['type'][0]
                assessment_group_level.last_assessment_level = last_assessment['level'][0]
                Individual_current_assessment_level.archive = False
                Individual_current_assessment_level.active = False
 
                if percentage >= 75:
                    Individual_last_assessment_level.archive = True
                    Individual_last_assessment_level.active = True
                    Individual_last_assessment_level.save()

            assessment_group_level.save()
            assessment_level.save()
            Individual_current_assessment_level.save()

            summarylog = ContentSummaryLog.objects.get(
                    content_id = assessment_id,
                    user=user_id,
            )
            summarylog = summarylog.id

            masterylogs = MasteryLog.objects.get(
                    summarylog=summarylog,
                    user=user_id,
            )

            if masterylogs:
                models.AssessmentHistory.objects.create(
                    user_id = masterylogs.user_id, 
                    summarylog_id=masterylogs.summarylog_id, 
                    assessment_id=assessment_id,
                    mastery_criterion=masterylogs.mastery_criterion,
                    start_timestamp=masterylogs.start_timestamp,
                    end_timestamp=masterylogs.end_timestamp,
                    completion_timestamp=masterylogs.completion_timestamp,
                    mastery_level=masterylogs.mastery_level,
                    complete=masterylogs.complete,
                    time_spent=masterylogs.time_spent,
                    question_sources = assessment_level.previous_question_sources
                    )
                
                assessment_update = models.ExamAssessment.objects.get(id=assessment_id)

                if assessment_update.extra_data['type'] == AssessmentConstant.PRE_TEST:
                    assessment_update.archive = True
                
                assessment_update.previous_question_sources = []
                assessment_update.save()

            return Response({"message": "Assessment marked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def process_assessment_list(self, assessments, current_assessment_id, last_assessment_id, score):
        for i, assessment in enumerate(assessments):
            if assessment["id"] == current_assessment_id:
                if "PRE" in assessment["type"]:
                    if score >= 75:
                        # If PreTest score is >= 75%, move to next PreTest
                        next_index = i + 1
                        while next_index < len(assessments):
                            next_assessment = assessments[next_index]
                            if "PRE" in next_assessment["type"]:
                                return next_assessment["id"], current_assessment_id, False
                            next_index += 1
                        # If no more PreTests, mark as last assessment and archive
                        return assessment["id"], last_assessment_id, True
                    else:
                        # If PreTest score < 75%, move to immediate next assessment
                        next_index = i + 1
                        if next_index < len(assessments):
                            next_assessment = assessments[next_index]
                            return next_assessment["id"], assessment["id"], False
                        else:
                            # Mark as last assessment and archive
                            return assessment["id"], last_assessment_id, True
                elif "POST" in assessment["type"]:
                    if score >= 75:
                        # If Post test score is >= 75%, move to next assessment
                        next_index = i + 1
                        if next_index < len(assessments):
                            next_assessment = assessments[next_index]
                            return next_assessment["id"], assessment["id"], False
                        else:
                            # Mark as last assessment and archive
                            return assessment["id"], last_assessment_id, True
                    else:
                        # If Post test score < 75%, no change until score >= 75%
                        return current_assessment_id, last_assessment_id, False
                else:
                    if score >= 75:
                        # If score >= 75%, move to next Level-Section
                        next_index = i + 1
                        while next_index < len(assessments):
                            next_assessment = assessments[next_index]
                            if "PRE" in next_assessment["type"]:
                                # If next assessment is PreTest, mark as last assessment and archive
                                return assessment["id"], last_assessment_id, True
                            elif "SECTION" in next_assessment["type"] or "POST" in next_assessment["type"]:
                                # If next assessment is Level-Section or Post test, update current and last assessment ids
                                return next_assessment["id"], assessment["id"], False
                            next_index += 1
                        # If no more assessments, mark as last assessment and archive
                        return assessment["id"], last_assessment_id, True
                    else:
                        # If score < 75%, no change until score >= 75%
                        return current_assessment_id, last_assessment_id, False
        # If current assessment id is not found in the list, return None for both ids
        return None, None, False

class AssessmentReportViewSet(ViewSet):

    def retrieve(self, request, pk=None):
        try:

            get_assessment = models.ExamAssessment.objects.get(id = pk)

            if get_assessment:
                
                assessment_data = {
                        'assessment_id': [get_assessment.id],
                        'question_count': [get_assessment.question_count],
                        'question_sources': [get_assessment.question_sources],
                        'user_id': [get_assessment.learner_id],
                       
                    }

                get_assessment_df = pd.DataFrame(assessment_data)
                
                content_session_logs = ContentSessionLog.objects.filter(content_id=pk, user_id=get_assessment.learner_id).values('id', 'content_id', 'start_timestamp', 'time_spent', 'user_id')
                
                if content_session_logs:
                    
                    content_session_logs_df = pd.DataFrame(content_session_logs)

                    list_of_session_ids = content_session_logs_df['id'].to_list()

                    content_session_logs_df = content_session_logs_df.rename(columns={'id': "sessionlog_id"})

                    attempt_logs = AttemptLog.objects.filter(sessionlog_id__in = list_of_session_ids).values("item", "correct", "user_id","sessionlog_id")
                    
                    if not attempt_logs:
                        return Response({"message": "No Assessment Attempted for this learner"}, status=status.HTTP_404_NOT_FOUND)
                    
                    attempt_logs_list_df = pd.DataFrame(attempt_logs)

                    attempt_logs_list_df['item'] = attempt_logs_list_df["item"].str.split(":").str[1]

                    correct_attempts_df = attempt_logs_list_df[attempt_logs_list_df['correct'] == 1]

                    assessment_session_df = pd.merge(content_session_logs_df, get_assessment_df, on='user_id').reset_index(drop=True)

                    assessment_session_df['correct_questions_ids'] = None
                    assessment_session_df['corrected_question_count'] = 0
                    attempt_count_list = [] 

                    for index, rows in assessment_session_df.iterrows():
                        attempt_count_list.append(index + 1)
                        
                        corrected_question_ids = correct_attempts_df[correct_attempts_df['sessionlog_id'] == rows['sessionlog_id']].reset_index(drop=True)

                        if corrected_question_ids.empty:
                            continue
                            
                        corrected_question_ids_list = corrected_question_ids['item'].tolist()
         
                        if len(corrected_question_ids) == len(corrected_question_ids_list):
                            assessment_session_df.at[index, 'correct_questions_ids'] = corrected_question_ids_list
                            assessment_session_df.at[index, 'corrected_question_count'] = len(corrected_question_ids_list)
                        
                        else:
                            assessment_session_df.at[index, 'correct_questions_ids'] = None
                    
                    assessment_session_df['attempt_count'] = attempt_count_list
                    assessment_session_df['start_timestamp'] = assessment_session_df['start_timestamp'].dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                    json_string = assessment_session_df.to_json(orient='records')
                    json_data = json.loads(json_string.replace("\\", ""))

                    return Response(json_data)
                
                return Response({"message": "No Session Available for this learner"}, status=status.HTTP_404_NOT_FOUND)
        
        except models.ExamAssessment.DoesNotExist:
            return Response({"error": "Assessment group not found"}, status=status.HTTP_404_NOT_FOUND)
