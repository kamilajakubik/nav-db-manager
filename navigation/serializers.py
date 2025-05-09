from rest_framework import serializers

from navigation.models import (
    Airport,
    Procedure,
    Navaid,
    ProcedureLeg,
    ProcedureTransition,
    Waypoint,
    Airway,
    AirwaySegment,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = [
            "id",
            "cycle",
            "airport_id",
            "icao_code",
            "name",
            "city",
            "state",
            "country",
            "latitude",
            "longitude",
            "elevation",
            "magnetic_variation",
            "transition_altitude",
            "transition_level",
            "longest_runway",
        ]


class ProcedureLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureLeg
        fields = [
            "sequence_number",
            "waypoint_identifier",
            "waypoint_type",
            "latitude",
            "longitude",
            "altitude_constraint",
            "speed_constraint",
            "course",
            "distance",
            "leg_type",
        ]


class ProcedureTransitionSerializer(serializers.ModelSerializer):
    legs = ProcedureLegSerializer(many=True, read_only=True)

    class Meta:
        model = ProcedureTransition
        fields = ["transition_id", "legs"]


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = ["id", "cycle", "airport", "procedure_id", "procedure_type"]


class NavaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navaid
        fields = [
            "id",
            "cycle",
            "navaid_id",
            "name",
            "navaid_type",
            "latitude",
            "longitude",
            "frequency",
            "elevation",
            "magnetic_variation",
            "dme_latitude",
            "dme_longitude",
            "dme_elevation",
            "service_volume",
        ]


class WaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waypoint
        fields = [
            "id",
            "cycle",
            "waypoint_id",
            "name",
            "waypoint_type",
            "latitude",
            "longitude",
            "airspace_classification",
        ]


class AirwaySegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirwaySegment
        fields = [
            "id",
            "sequence_number",
            "fix_identifier",
            "fix_type",
            "next_fix_identifier",
            "next_fix_type",
            "route_distance",
            "maximum_altitude",
            "magnetic_course",
            "reverse_magnetic_course",
        ]


class AirwaySerializer(serializers.ModelSerializer):
    segments_count = serializers.IntegerField(source="segments.count", read_only=True)

    class Meta:
        model = Airway
        fields = ["id", "cycle", "airway_id", "route_type", "segments_count"]
