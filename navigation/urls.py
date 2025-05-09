from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register("airports", views.AirportViewSet)
router.register("navaids", views.NavaidViewSet)
router.register("procedures", views.ProcedureViewSet)
router.register("waypoints", views.WaypointViewSet)
router.register("airways", views.AirwayViewSet)

urlpatterns = router.urls
