from django.conf.urls import include
from django.conf.urls import url
from rest_framework import routers

from .api import AssessmentViewset

router = routers.SimpleRouter()
router.register(r"assessment", AssessmentViewset, basename="assessment")

urlpatterns = [url(r"^", include(router.urls))]
