from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register("airports", views.AirportViewSet, basename="airport")
router.register("navaids", views.NavaidViewSet, basename="navaid")
router.register("procedures", views.ProcedureViewSet, basename="procedure")
router.register("waypoints", views.WaypointViewSet, basename="waypoint")
router.register("airways", views.AirwayViewSet, basename="airway")

urlpatterns = router.urls
