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


class AirportViewSet(ReadOnlyModelViewSet):
    latest_cycle = DataCycle.objects.order_by("-effective_date").first()
    queryset = Airport.objects.filter(cycle=latest_cycle).all()
    serializer_class = AirportSerializer

    @action(detail=True, methods=["get"])
    def procedures(self, request, pk=None):
        airport = self.get_object()
        procedures = airport.procedures
        if not procedures.exists():
            return Response({"detail": "No procedures found for this airport."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NavaidViewSet(ReadOnlyModelViewSet):
    latest_cycle = DataCycle.objects.order_by("-effective_date").first()
    queryset = Navaid.objects.filter(cycle=latest_cycle).all()
    serializer_class = NavaidSerializer


class ProcedureViewSet(ReadOnlyModelViewSet):
    latest_cycle = DataCycle.objects.order_by("-effective_date").first()
    queryset = Procedure.objects.filter(cycle=latest_cycle).all()
    serializer_class = ProcedureSerializer

    @action(detail=True, methods=["get"])
    def legs(self, request, pk=None):
        transitions = ProcedureTransition.objects.filter(procedure__id=pk)
        if not transitions.exists():
            return Response({"detail": "No transitions found for this procedure."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProcedureTransitionSerializer(transitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WaypointViewSet(ReadOnlyModelViewSet):
    latest_cycle = DataCycle.objects.order_by("-effective_date").first()
    queryset = Waypoint.objects.filter(cycle=latest_cycle).all()
    serializer_class = WaypointSerializer


class AirwayViewSet(ReadOnlyModelViewSet):
    latest_cycle = DataCycle.objects.order_by("-effective_date").first()
    queryset = Airway.objects.filter(cycle=latest_cycle).all()
    serializer_class = AirwaySerializer

    @action(detail=True, methods=["get"])
    def segments(self, request, pk=None):
        airway = self.get_object()
        segments = airway.segments
        if not segments.exists():
            return Response({"detail": "No segments found for this airway."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AirwaySegmentSerializer(segments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
