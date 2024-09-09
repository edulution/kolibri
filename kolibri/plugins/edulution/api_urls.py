from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers

from .viewsets import LearnerClassroomViewset
from .viewsets import LearnerLessonViewset
from .viewsets import LearnHomePageHydrationView
from .viewsets import LearnStateView
from .viewsets import LearnerGroupViewset

router = routers.SimpleRouter()
router.register(
    r"learnerclassroom", LearnerClassroomViewset, basename="learnerclassroom"
)
router.register(r"learnerlesson", LearnerLessonViewset, basename="learnerlesson")
router.register(r"learnergroup", LearnerGroupViewset, basename="learnergroup")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"state", LearnStateView.as_view(), name="state"),
    url(r"homehydrate", LearnHomePageHydrationView.as_view(), name="homehydrate"),
]
