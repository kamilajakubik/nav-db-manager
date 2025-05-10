from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from navigation.models import Airport, DataCycle, Navaid, Procedure, ProcedureTransition, ProcedureLeg, Waypoint, Airway
from navigation.serializers import (
    AirportSerializer,
    ProcedureSerializer,
    NavaidSerializer,
    ProcedureTransitionSerializer,
    WaypointSerializer,
    AirwaySerializer,
    AirwaySegmentSerializer,
)


class LatestCycleQueryMixin:
    def get_latest_cycle(self):
        return DataCycle.objects.order_by("-effective_date").first()

    def filter_by_latest_cycle(self, queryset):
        return queryset.filter(cycle=self.get_latest_cycle())


class AirportViewSet(LatestCycleQueryMixin, ReadOnlyModelViewSet):
    serializer_class = AirportSerializer

    def get_queryset(self):
        return self.filter_by_latest_cycle(Airport.objects.all())

    @action(detail=True, methods=["get"])
    def procedures(self, request, pk=None):
        airport = self.get_object()
        procedures = airport.procedures
        if not procedures.exists():
            return Response({"detail": "No procedures found for this airport."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NavaidViewSet(LatestCycleQueryMixin, ReadOnlyModelViewSet):
    serializer_class = NavaidSerializer

    def get_queryset(self):
        return self.filter_by_latest_cycle(Navaid.objects.all())


class ProcedureViewSet(LatestCycleQueryMixin, ReadOnlyModelViewSet):
    serializer_class = ProcedureSerializer

    def get_queryset(self):
        return self.filter_by_latest_cycle(Procedure.objects.all())

    @action(detail=True, methods=["get"])
    def legs(self, request, pk=None):
        transitions = ProcedureTransition.objects.filter(procedure__id=pk)
        if not transitions.exists():
            return Response({"detail": "No transitions found for this procedure."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProcedureTransitionSerializer(transitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WaypointViewSet(LatestCycleQueryMixin, ReadOnlyModelViewSet):
    serializer_class = WaypointSerializer

    def get_queryset(self):
        return self.filter_by_latest_cycle(Waypoint.objects.all())


class AirwayViewSet(LatestCycleQueryMixin, ReadOnlyModelViewSet):
    serializer_class = AirwaySerializer

    def get_queryset(self):
        return self.filter_by_latest_cycle(Airway.objects.all())

    @action(detail=True, methods=["get"])
    def segments(self, request, pk=None):
        airway = self.get_object()
        segments = airway.segments
        if not segments.exists():
            return Response({"detail": "No segments found for this airway."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AirwaySegmentSerializer(segments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
