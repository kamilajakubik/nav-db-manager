from django.db import models

class DataCycle(models.Model):
    cycle_id = models.CharField(max_length=10, primary_key=True)
    effective_date = models.DateField()
    expiry_date = models.DateField()
    source = models.CharField(max_length=100)

    class Meta:
        ordering = ['-effective_date']

class Coordinates(models.Model):
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)

    class Meta:
        abstract = True

class Airport(Coordinates):
    cycle = models.ForeignKey(DataCycle, on_delete=models.CASCADE)
    airport_id = models.CharField(max_length=10)
    icao_code = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, null=True, blank=True)
    country = models.CharField(max_length=2)
    elevation = models.IntegerField()  # In feet
    magnetic_variation = models.CharField(max_length=5)
    transition_altitude = models.IntegerField(null=True, blank=True)
    transition_level = models.IntegerField(null=True, blank=True)
    longest_runway = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.icao_code} - {self.name}"

class Navaid(Coordinates):
    NAVAID_TYPES = [
        ('VOR', 'VOR'),
        ('DME', 'DME'),
        ('VOR/DME', 'VOR/DME'),
        ('VORTAC', 'VORTAC'),
        ('TACAN', 'TACAN'),
        ('NDB', 'NDB'),
        ('NDB/DME', 'NDB/DME'),
        ('LOC', 'Localizer'),
        ('GP', 'Glide Path'),
        ('TCN', 'TACAN'),
    ]
    cycle = models.ForeignKey(DataCycle, on_delete=models.CASCADE)
    navaid_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    navaid_type = models.CharField(max_length=10, choices=NAVAID_TYPES)
    frequency = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    elevation = models.IntegerField(null=True, blank=True)  # In feet
    magnetic_variation = models.CharField(max_length=5, null=True, blank=True)
    dme_latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    dme_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    dme_elevation = models.IntegerField(null=True, blank=True)  # In feet
    service_volume = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.navaid_id} - {self.name} - {self.navaid_type}"

class Waypoint(Coordinates):
    WAYPOINT_TYPES = [
        ('ENROUTE', 'Enroute'),
        ('TERMINAL', 'Terminal'),
        ('IAF', 'Initial Approach Fix'),
        ('IF', 'Intermediate Fix'),
        ('FAF', 'Final Approach Fix'),
        ('MAP', 'Missed Approach Point'),
    ]
    cycle = models.ForeignKey(DataCycle, on_delete=models.CASCADE)
    waypoint_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    waypoint_type = models.CharField(max_length=10, choices=WAYPOINT_TYPES)
    airspace_classification = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return f"{self.waypoint_id} - {self.name}"

class Airway(models.Model):
    ROUTE_TYPES = [
        ('JETWAY', 'Jet Route'),
        ('VICTOR', 'Victor Airway'),
        ('RNAV', 'RNAV Route'),
        ('HELICOPTER', 'Helicopter Route'),
    ]
    cycle = models.ForeignKey(DataCycle, on_delete=models.CASCADE)
    airway_id = models.CharField(max_length=10)
    route_type = models.CharField(max_length=10, choices=ROUTE_TYPES)

    def __str__(self):
        return f"{self.airway_id} - {self.route_type}"

class AirwaySegment(models.Model):
    FIX_TYPES = [
        ("WAYPOINT", "Waypoint"),
        ("NAVAID", "Navaid"),
        ("AIRPORT", "Airport"),
    ]

    airway = models.ForeignKey(Airway, on_delete=models.CASCADE, related_name="segments")
    sequence_number = models.IntegerField()
    fix_identifier = models.CharField(max_length=10)
    fix_type = models.CharField(max_length=10, choices=FIX_TYPES)
    next_fix_identifier = models.CharField(max_length=10, null=True, blank=True)
    next_fix_type = models.CharField(max_length=10, choices=FIX_TYPES, null=True, blank=True)
    route_distance = models.IntegerField(null=True, blank=True)  # In nautical miles
    minimum_altitude = models.IntegerField(null=True, blank=True)  # In feet
    maximum_altitude = models.IntegerField(null=True, blank=True)  # In feet
    magnetic_course = models.IntegerField(null=True, blank=True)
    reverse_magnetic_course = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.airway.airway_id} - segment {self.sequence_number}"

class Procedure(models.Model):
    PROCEDURE_TYPES = [
        ("SID", "Standard Instrument Departure"),
        ("STAR", "Standard Terminal Arrival Route"),
        ("APPROACH", "Instrument Approach"),
    ]
    cycle = models.ForeignKey(DataCycle, on_delete=models.CASCADE)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="procedures")
    procedure_id = models.CharField(max_length=10)
    procedure_type = models.CharField(max_length=10, choices=PROCEDURE_TYPES)

    def __str__(self):
        return f"{self.airport.icao_code} - {self.procedure_id} - {self.procedure_type}"

class ProcedureTransition(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name="transitions")
    transition_id = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.procedure.procedure_id} - {self.transition_id}"

class ProcedureLeg(Coordinates):
    WAYPOINT_TYPES = [
        ("WAYPOINT", "Waypoint"),
        ("NAVAID", "Navaid"),
        ("IAF", "Initial Approach Fix"),
        ("IF", "Intermediate Fix"),
        ("FAF", "Final Approach Fix"),
        ("MAP", "Missed Approach Point"),
    ]

    transition = models.ForeignKey(ProcedureTransition, on_delete=models.CASCADE, related_name="legs")
    sequence_number = models.IntegerField()
    waypoint_identifier = models.CharField(max_length=10)
    waypoint_type = models.CharField(max_length=10, choices=WAYPOINT_TYPES)
    altitude_constraint = models.CharField(max_length=50, null=True, blank=True)
    speed_constraints = models.CharField(max_length=50, null=True, blank=True)
    course = models.IntegerField(null=True, blank=True)
    distance = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    leg_type = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.transition.procedure.procedure_id} - {self.transition.transition_id} - leg {self.sequence_number}"


