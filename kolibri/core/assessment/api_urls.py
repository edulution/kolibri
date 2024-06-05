from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers

from .api import AssessmentViewset, GroupAssessmentViewset, CreateAssessmentRecord, ExamAssessmentStartViewSet, ExamAssessmentStopViewSet, GetAssessmentViewSet
from .api import GetLearnerAssessmentViewset, FetchAssessmentGroupData, MarkAssessmentViewset, AssessmentTestViewSet, AssessmentReportViewSet,AssessmentHistoryReportViewSet

router = routers.SimpleRouter()
router.register(r"assessment", CreateAssessmentRecord, basename="assessment")
router.register(r"assessmentdetails", AssessmentViewset, basename="assessmentdetails")
router.register(r"assessmentgroup", GroupAssessmentViewset, basename="assessmentgroup")
router.register(r"assessmentstart", ExamAssessmentStartViewSet, basename="assessmentstart")
router.register(r"assessmentstop", ExamAssessmentStopViewSet, basename="assessmentstop")
router.register(r"learnerassessments", GetLearnerAssessmentViewset, basename="learnerassessments")
router.register(r"fetchbyassessmentgroupid", FetchAssessmentGroupData, basename="fetchassessmentdata")
router.register(r"markassessment", MarkAssessmentViewset, basename="markassessment")
router.register(r"assessmenttest", AssessmentTestViewSet, basename="assessmenttest")
router.register(r"assessmentpastreport", AssessmentReportViewSet, basename="assessmentpastreport")
router.register(r"assessmenthistoryreport", AssessmentHistoryReportViewSet, basename="assessmenthistoryreport")
router.register(r"getassessment", GetAssessmentViewSet, basename="getassessment")

urlpatterns = [url(r"^", include(router.urls))]
