import json

from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone

from .permissions import UserCanReadExamAssignmentData
from .permissions import UserCanReadExamData
from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import AbstractFacilityDataModel
from kolibri.core.auth.models import Collection
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import FacilityDataset
from kolibri.core.auth.permissions.base import RoleBasedPermissions
from kolibri.core.content.utils.assignment import ContentAssignmentManager
from kolibri.core.fields import JSONField
from kolibri.core.notifications.models import LearnerProgressNotification


def exam_assignment_lookup(question_sources):
    """
    Lookup function for the ContentAssignmentManager
    :param question_sources: a list of dicts from an Exam
    :return: a tuple of contentnode_id and metadata
    """
    for question_source in question_sources:
        yield (question_source["exercise_id"], None)


class ExamAssessment(AbstractFacilityDataModel):
    """
    This class stores metadata about teacher-created quizzes to test current student knowledge.
    """

    morango_model_name = "examassessment"

    permissions = (
        RoleBasedPermissions(
            target_field="collection",
            can_be_created_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_read_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_updated_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_deleted_by=(role_kinds.ADMIN, role_kinds.COACH),
        )
        | UserCanReadExamData()
    )

    title = models.CharField(max_length=200)

    # Total number of questions in the exam. Equal to the length of the question_sources array.
    question_count = models.IntegerField()

    question_sources = JSONField(default=[], blank=True)

    seed = models.IntegerField(default=1)

    assignments = JSONField(default=[], blank=True)

    channel_id = models.UUIDField(null=True)

    # When True, learners see questions in the order they appear in 'question_sources'.
    # When False, each learner sees questions in a random (but consistent) order seeded
    #   by their user's UUID.
    learners_see_fixed_order = models.BooleanField(default=False)

    # Is this exam currently active and visible to students to whom it is assigned?
    active = models.BooleanField(default=False)

    # Exams are scoped to a particular class (usually) as they are associated with a Coach
    # who creates them in the context of their class, this stores that relationship but does
    # not assign exam itself to the class - for that see the ExamAssignment model.
    collection = models.ForeignKey(
        Collection, related_name="examassessment", blank=False, null=False
    )

    learner = models.ForeignKey(
        FacilityUser, related_name="examassessmentlearner", blank=False, null=True
    )

    creator = models.ForeignKey(
        FacilityUser, related_name="examassessment", blank=False, null=True
    )
    assessment_group = models.ForeignKey(
        'ExamAssessmentGroup',  # String reference to the model
        related_name="exam_assessments",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    # To be set True when the quiz is first set to active=True
    date_activated = models.DateTimeField(default=None, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, null=True)

    # archive will be used on the frontend to indicate if a quiz is "closed"
    archive = models.BooleanField(default=False)
    date_archived = models.DateTimeField(default=None, null=True, blank=True)

    content_assignments = ContentAssignmentManager(
        # one exam can contain multiple questions from multiple exercises,
        # hence multiple content nodes
        one_to_many=True,
        filters=dict(active=True),
        lookup_field="question_sources",
        lookup_func=exam_assignment_lookup,
    )

    def delete(self, using=None, keep_parents=False):
        """
        We delete all notifications objects whose quiz is this exam id.
        """
        LearnerProgressNotification.objects.filter(quiz_id=self.id).delete()
        super(ExamAssessment, self).delete(using, keep_parents)

    def pre_save(self):
        super(ExamAssessment, self).pre_save()

        # maintain stricter enforcement on when creator is allowed to be null
        if self._state.adding and self.creator is None:
            raise IntegrityError("Exam must be saved with an creator")

        # validate that datasets match so this would be syncable
        if self.creator and self.creator.dataset_id != self.dataset_id:
            # the only time creator can be null is if it's a superuser
            # and if we set it to none HERE
            if not self.creator.is_superuser:
                raise IntegrityError("Exam must have creator in the same dataset")
            self.creator = None

    def save(self, *args, **kwargs):
        # If archive is True during the save op, but there is no date_archived then
        # this is the save that is archiving the object and we need to datestamp it
        if getattr(self, "archive", False) is True:
            if getattr(self, "date_archived") is None:
                self.date_archived = timezone.now()
        super(ExamAssessment, self).save(*args, **kwargs)

    """
    As we evolve this model in ways that migrations can't handle, certain fields may
    become deprecated, and other fields may need to be interpreted differently. This
    may happen when multiple versions of the model need to coexist in the same database.

    The 'data_model_version' field is used to keep track of the version of the model.

    Certain fields that are only relevant for older model versions get prefixed
    with their version numbers.
    """
    data_model_version = models.SmallIntegerField(default=2)

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("collection")

    def calculate_partition(self):
        return self.dataset_id

    def __str__(self):
        return self.title


class ExamAssignmentAssessment(AbstractFacilityDataModel):
    """
    This class acts as an intermediary to handle assignment of an exam to particular collections
    classes, groups, etc.
    """

    morango_model_name = "examassignmentassessment"

    permissions = (
        RoleBasedPermissions(
            target_field="collection",
            can_be_created_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_read_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_updated_by=(),
            can_be_deleted_by=(role_kinds.ADMIN, role_kinds.COACH),
        )
        | UserCanReadExamAssignmentData()
    )
    exam = models.ForeignKey(ExamAssessment, related_name="assignmentassessments", blank=False, null=False)
    collection = models.ForeignKey(
        Collection, related_name="assessment_exams", blank=False, null=False
    )
    assigned_by = models.ForeignKey(
        FacilityUser, related_name="assessment_exams", blank=False, null=True
    )

    def pre_save(self):
        super(ExamAssignmentAssessment, self).pre_save()

        # this shouldn't happen
        if (
            self.exam
            and self.collection
            and self.exam.dataset_id != self.collection.dataset_id
        ):
            raise IntegrityError(
                "Exam assignment foreign models must be in same dataset"
            )

        # maintain stricter enforcement on when assigned_by is allowed to be null
        # assignments aren't usually updated, but ensure only during creation
        if self._state.adding and self.assigned_by is None:
            raise IntegrityError("Exam assignment must be saved with an assigner")

        # validate that datasets match so this would be syncable
        if self.assigned_by and self.assigned_by.dataset_id != self.dataset_id:
            # the only time assigned_by can be null is if it's a superuser
            # and if we set it to none HERE
            if not self.assigned_by.is_superuser:
                # maintain stricter enforcement on when assigned_by is allowed to be null
                raise IntegrityError(
                    "Exam assignment must have assigner in the same dataset"
                )
            self.assigned_by = None

    def infer_dataset(self, *args, **kwargs):
        # infer from exam so assignments align with exams
        return self.cached_related_dataset_lookup("exam")

    def calculate_source_id(self):
        return "{exam_id}:{collection_id}".format(
            exam_id=self.exam_id, collection_id=self.collection_id
        )

    def calculate_partition(self):
        return self.dataset_id


def individual_exam_assignment_lookup(serialized_exam):
    """
    Lookup function for the ContentAssignmentManager
    :param serialized_exam: the exam in form of a dictionary
    :return: a tuple of contentnode_id and metadata
    """
    try:
        question_sources = json.loads(serialized_exam.get("question_sources", "[]"))
        return exam_assignment_lookup(question_sources)
    except json.JSONDecodeError:
        return []


class IndividualSyncableExam(AbstractFacilityDataModel):
    """
    Represents a Exam and its assignment to a particular user
    in such a way that it can be synced to a single-user device.
    Note: This is not the canonical representation of a user's
    relation to an exam (which is captured in an ExamAssignment
    combined with a user's Membership in an associated Collection;
    the purpose of this model is as a derived/denormalized
    representation of a specific user's exam assignments).
    """

    morango_model_name = "individualsyncableexam"

    user = models.ForeignKey(FacilityUser, related_name='individual_syncable_exams_assessment')
    collection = models.ForeignKey(Collection, related_name='individual_syncable_exams_assessment')
    dataset = models.ForeignKey(FacilityDataset, related_name="individual_syncable_exams_assessment")
    exam_id = models.UUIDField()

    serialized_exam = JSONField()

    content_assignments = ContentAssignmentManager(
        # one exam can contain multiple questions from multiple exercises,
        # hence multiple content nodes
        one_to_many=True,
        lookup_field="serialized_exam",
        lookup_func=individual_exam_assignment_lookup,
    )

    def infer_dataset(self, *args, **kwargs):
        return self.cached_related_dataset_lookup("user")

    def calculate_source_id(self):
        return self.exam_id

    def calculate_partition(self):
        return "{dataset_id}:user-ro:{user_id}".format(
            dataset_id=self.dataset_id, user_id=self.user_id
        )

    @classmethod
    def serialize_exam(cls, exam):
        serialized = exam.serialize()
        for key in [
            "active",
            "creator_id",
            "date_created",
            "date_activated",
            "collection_id",
        ]:
            serialized.pop(key, None)
        return serialized

    @classmethod
    def deserialize_exam(cls, serialized_exam):
        exam = ExamAssessment.deserialize(serialized_exam)
        exam.active = True
        return exam
    

class ExamAssessmentGroup(models.Model):

    morango_model_name = "examassessmentgroup"

    permissions = (
        RoleBasedPermissions(
            target_field="collection",
            can_be_created_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_read_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_updated_by=(role_kinds.ADMIN, role_kinds.COACH),
            can_be_deleted_by=(role_kinds.ADMIN, role_kinds.COACH),
        )
        | UserCanReadExamData()
    )

    title = models.CharField(max_length=200)

    learner_id = models.CharField(max_length=200, default='1')

    channel_id = models.UUIDField(null=True)
    new_id = models.UUIDField(null=True)

    # Is this exam currently active and visible to students to whom it is assigned?
    active = models.BooleanField(default=False)

    creator = models.ForeignKey(
        FacilityUser, related_name="assessementfacilityuser", blank=False, null=True
    )

    collection = models.ForeignKey(
        Collection, related_name="examassessmentgrouplist", blank=False, null=True
    )

    date_activated = models.DateTimeField(default=None, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    archive = models.BooleanField(default=False)
    date_archived = models.DateTimeField(default=None, null=True, blank=True)
    assessment_map  = JSONField(default=[], blank=True)
    last_assessment = models.ForeignKey(
        'ExamAssessment',  # String reference to the model
        related_name="last_assessment_group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    current_assessment = models.ForeignKey(
        'ExamAssessment',  # String reference to the model
        related_name="current_assessment_group",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

