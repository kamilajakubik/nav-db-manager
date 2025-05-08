import logging
from xml.etree.ElementTree import Element

from navigation.models import (
    Airport,
    Airway,
    AirwaySegment,
    DataCycle,
    Navaid,
    Procedure,
    Waypoint,
    ProcedureTransition,
    ProcedureLeg,
)


class ARINCParser:
    def __init__(self, data_cycle: DataCycle):
        self.data_cycle = data_cycle
        self.logger = logging.getLogger(__name__)

    def parse_file(self, root: Element):
        """Parse the ARINC 424 XML file.

        Args:
            root: The root element of the XML document.

        Raises:
            ValueError: If required elements are missing or malformed.

        """
        self._parse_airports(root.find("AIRPORTS"))
        self._parse_navaids(root.find("NAVAIDS"))
        self._parse_waypoints(root.find("WAYPOINTS"))
        self._parse_airways(root.find("AIRWAYS"))
        self._parse_procedures(root.find("PROCEDURES"))

    def _parse_airports(self, airports_element: Element):
        """Parse airport data from the XML.

        Args:
            airports_element: The XML element containing airport data.
        """
        if airports_element is None:
            self.logger.warning("No airports element found in the XML file")
            return

        self.logger.info("Parsing airport elements...")
        for airport_elem in airports_element.findall("AIRPORT"):
            airport_id = airport_elem.find("AIRPORT_IDENTIFIER").text
            try:
                airport, created = Airport.objects.get_or_create(
                    cycle=self.data_cycle,
                    airport_id=airport_id,
                    defaults={
                        "icao_code": airport_elem.find("ICAO_CODE").text,
                        "name": airport_elem.find("AIRPORT_NAME").text,
                        "city": airport_elem.find("CITY_NAME").text,
                        "state": airport_elem.find("STATE_CODE").text
                        if airport_elem.find("STATE_CODE") is not None
                        else None,
                        "country": airport_elem.find("COUNTRY_CODE").text,
                        "latitude": float(airport_elem.find(".//LATITUDE").text),
                        "longitude": float(airport_elem.find(".//LONGITUDE").text),
                        "elevation": int(airport_elem.find("ELEVATION").text),
                        "magnetic_variation": airport_elem.find("MAGNETIC_VARIATION").text,
                        "transition_altitude": int(airport_elem.find("TRANSITION_ALTITUDE").text)
                        if airport_elem.find("TRANSITION_ALTITUDE") is not None
                        else None,
                        "transition_level": int(airport_elem.find("TRANSITION_LEVEL").text)
                        if airport_elem.find("TRANSITION_LEVEL") is not None
                        else None,
                        "longest_runway": int(airport_elem.find("LONGEST_RUNWAY").text)
                        if airport_elem.find("LONGEST_RUNWAY") is not None
                        else None,
                    },
                )
            except Exception:
                self.logger.error(f"Unable to parse data for airport {airport_id}")
        self.logger.info("Parsing airports finished")

    def _parse_navaids(self, navaids_element: Element):
        if navaids_element is None:
            self.logger.warning("No navaids element found in the XML file")
            return

        self.logger.info("Parsing navaids elements...")
        for navaid_elem in navaids_element.findall("NAVAID"):
            navaid_id = navaid_elem.find("NAVAID_IDENTIFIER").text
            try:
                navaid, created = Navaid.objects.get_or_create(
                    cycle=self.data_cycle,
                    navaid_id=navaid_id,
                    defaults={
                        "name": navaid_elem.find("NAVAID_NAME").text,
                        "navaid_type": navaid_elem.find("NAVAID_TYPE").text,
                        "frequency": float(navaid_elem.find("NAVAID_FREQUENCY").text)
                        if navaid_elem.find("NAVAID_FREQUENCY") is not None
                        else None,
                        "latitude": float(navaid_elem.find(".//LATITUDE").text),
                        "longitude": float(navaid_elem.find(".//LONGITUDE").text),
                        "elevation": int(navaid_elem.find("ELEVATION").text)
                        if navaid_elem.find("ELEVATION") is not None
                        else None,
                        "magnetic_variation": navaid_elem.find("MAGNETIC_VARIATION").text
                        if navaid_elem.find("MAGNETIC_VARIATION") is not None
                        else None,
                        "dme_position_latitude": float(navaid_elem.find(".//DME_POSITION/LATITUDE").text)
                        if navaid_elem.find(".//DME_POSITION") is not None
                        else None,
                        "dme_position_longitude": float(navaid_elem.find(".//DME_POSITION/LONGITUDE").text)
                        if navaid_elem.find(".//DME_POSITION") is not None
                        else None,
                        "dme_elevation": int(navaid_elem.find(".//DME_POSITION/ELEVATION").text)
                        if navaid_elem.find(".//DME_POSITION/ELEVATION") is not None
                        else None,
                        "service_volume": navaid_elem.find("SERVICE_VOLUME").text
                        if navaid_elem.find("SERVICE_VOLUME") is not None
                        else None,
                    },
                )
            except Exception:
                self.logger.error(f"Unable to parse data for navaid {navaid_id}")
        self.logger.info("Parsing navaids finished")

    def _parse_waypoints(self, waypoints_element: Element):
        if waypoints_element is None:
            self.logger.warning("No waypoints element found in the XML file")
            return

        self.logger.info("Parsing waypoints elements...")
        for waypoint_elem in waypoints_element.findall("WAYPOINT"):
            waypoint_id = waypoint_elem.find("WAYPOINT_IDENTIFIER").text
            try:
                waypoint, created = Waypoint.objects.get_or_create(
                    cycle=self.data_cycle,
                    waypoint_id=waypoint_id,
                    defaults={
                        "name": waypoint_elem.find("WAYPOINT_NAME").text,
                        "waypoint_type": waypoint_elem.find("WAYPOINT_TYPE").text,
                        "latitude": float(waypoint_elem.find(".//LATITUDE").text),
                        "longitude": float(waypoint_elem.find(".//LONGITUDE").text),
                        "airspace_classification": waypoint_elem.find("AIRSPACE_CLASSIFICATION").text
                        if waypoint_elem.find("AIRSPACE_CLASSIFICATION") is not None
                        else None,
                    },
                )
            except Exception:
                self.logger.error(f"Unable to parse data for waypoint {waypoint_id}")
        self.logger.info("Parsing waypoints finished")

    def _parse_airways(self, airways_element: Element):
        if airways_element is None:
            self.logger.warning("No airways element found in the XML file")
            return

        self.logger.info("Parsing airways elements...")
        for airway_elem in airways_element.findall("AIRWAY"):
            airway_id = airway_elem.find("ROUTE_IDENTIFIER").text
            try:
                airway, created = Airway.objects.get_or_create(
                    cycle=self.data_cycle,
                    airway_id=airway_id,
                    defaults={
                        "route_type": airway_elem.find("ROUTE_TYPE").text,
                    },
                )

                # Create the airway segment
                sequence_number = int(airway_elem.find("SEQUENCE_NUMBER").text)
                segment, created = AirwaySegment.objects.get_or_create(
                    airway=airway,
                    sequence_number=sequence_number,
                    defaults={
                        "fix_identifier": airway_elem.find("FIX_IDENTIFIER").text,
                        "fix_type": airway_elem.find("FIX_TYPE").text,
                        "next_fix_identifier": airway_elem.find("NEXT_FIX_IDENTIFIER").text
                        if airway_elem.find("NEXT_FIX_IDENTIFIER") is not None
                        else None,
                        "next_fix_type": airway_elem.find("NEXT_FIX_TYPE").text
                        if airway_elem.find("NEXT_FIX_TYPE") is not None
                        else None,
                        "route_distance": int(airway_elem.find("ROUTE_DISTANCE").text)
                        if airway_elem.find("ROUTE_DISTANCE") is not None
                        else None,
                        "minimum_altitude": int(airway_elem.find("MINIMUM_ALTITUDE").text)
                        if airway_elem.find("MINIMUM_ALTITUDE") is not None
                        else None,
                        "maximum_altitude": int(airway_elem.find("MAXIMUM_ALTITUDE").text)
                        if airway_elem.find("MAXIMUM_ALTITUDE") is not None
                        else None,
                        "magnetic_course": int(airway_elem.find("MAGNETIC_COURSE").text)
                        if airway_elem.find("MAGNETIC_COURSE") is not None
                        else None,
                        "reverse_magnetic_course": int(airway_elem.find("REVERSE_MAGNETIC_COURSE").text)
                        if airway_elem.find("REVERSE_MAGNETIC_COURSE") is not None
                        else None,
                    },
                )
            except Exception:
                self.logger.error(f"Unable to parse data for airway {airway_id}")
        self.logger.info("Parsing airways finished")

    def _parse_procedures(self, procedures_element: Element):
        if procedures_element is None:
            self.logger.warning("No procedures element found in the XML file")
            return

        # Process approaches
        self.logger.info("Parsing approaches elements...")
        for approach_elem in procedures_element.findall("APPROACH"):
            airport_id = approach_elem.find("AIRPORT_IDENTIFIER").text
            procedure_id = approach_elem.find("PROCEDURE_IDENTIFIER").text

            try:
                airport = Airport.objects.get(cycle=self.data_cycle, airport_id=airport_id)

                # Create the procedure
                procedure, created = Procedure.objects.get_or_create(
                    cycle=self.data_cycle,
                    airport=airport,
                    procedure_id=procedure_id,
                    defaults={
                        "procedure_type": "APPROACH",
                    },
                )

                # Create the transition
                transition_id = approach_elem.find("TRANSITION_IDENTIFIER").text
                transition, created = ProcedureTransition.objects.get_or_create(
                    procedure=procedure, transition_id=transition_id
                )

                # Create the leg
                sequence_number = int(approach_elem.find("SEQUENCE_NUMBER").text)
                waypoint_identifier = approach_elem.find("WAYPOINT_IDENTIFIER").text

                leg, created = ProcedureLeg.objects.get_or_create(
                    transition=transition,
                    sequence_number=sequence_number,
                    defaults={
                        "waypoint_identifier": waypoint_identifier,
                        "waypoint_type": approach_elem.find("WAYPOINT_TYPE").text,
                        "latitude": float(approach_elem.find(".//LATITUDE").text)
                        if approach_elem.find(".//POSITION") is not None
                        else None,
                        "longitude": float(approach_elem.find(".//LONGITUDE").text)
                        if approach_elem.find(".//POSITION") is not None
                        else None,
                        "altitude_constraint": approach_elem.find("ALTITUDE_CONSTRAINT").text
                        if approach_elem.find("ALTITUDE_CONSTRAINT") is not None
                        else None,
                        "speed_constraint": approach_elem.find("SPEED_CONSTRAINT").text
                        if approach_elem.find("SPEED_CONSTRAINT") is not None
                        else None,
                        "course": int(approach_elem.find("COURSE").text)
                        if approach_elem.find("COURSE") is not None
                        else None,
                        "distance": float(approach_elem.find("DISTANCE").text)
                        if approach_elem.find("DISTANCE") is not None
                        else None,
                    },
                )
            except Airport.DoesNotExist:
                self.logger.error(f"Airport with identifier {airport_id} not found!")
            self.logger.info("Parsing approaches finished")

            # Process SIDs
            self.logger.info("Parsing SIDs elements...")
            for sid_elem in procedures_element.findall("SID"):
                airport_id = sid_elem.find("AIRPORT_IDENTIFIER").text
                procedure_id = sid_elem.find("PROCEDURE_IDENTIFIER").text

                try:
                    airport = Airport.objects.get(cycle=self.data_cycle, airport_id=airport_id)

                    # Create the procedure
                    procedure, created = Procedure.objects.get_or_create(
                        cycle=self.data_cycle,
                        airport=airport,
                        procedure_id=procedure_id,
                        defaults={
                            "procedure_type": "SID",
                        },
                    )

                    # Create the transition
                    transition_id = sid_elem.find("TRANSITION_IDENTIFIER").text
                    transition, created = ProcedureTransition.objects.get_or_create(
                        procedure=procedure, transition_id=transition_id
                    )

                    # Create the leg
                    sequence_number = int(sid_elem.find("SEQUENCE_NUMBER").text)
                    waypoint_identifier = sid_elem.find("WAYPOINT_IDENTIFIER").text

                    leg, created = ProcedureLeg.objects.get_or_create(
                        transition=transition,
                        sequence_number=sequence_number,
                        defaults={
                            "waypoint_identifier": waypoint_identifier,
                            "waypoint_type": sid_elem.find("WAYPOINT_TYPE").text,
                            "altitude_constraint": sid_elem.find("ALTITUDE_CONSTRAINT").text
                            if sid_elem.find("ALTITUDE_CONSTRAINT") is not None
                            else None,
                            "speed_constraint": sid_elem.find("SPEED_CONSTRAINT").text
                            if sid_elem.find("SPEED_CONSTRAINT") is not None
                            else None,
                        },
                    )
                except Airport.DoesNotExist:
                    self.logger.error(f"Airport with identifier {airport_id} not found!")
                self.logger.info("Parsing SIDs finished")

            # Process STARs
            self.logger.info("Parsing STARs elements...")
            for star_elem in procedures_element.findall("STAR"):
                airport_id = star_elem.find("AIRPORT_IDENTIFIER").text
                procedure_id = star_elem.find("PROCEDURE_IDENTIFIER").text

                try:
                    airport = Airport.objects.get(cycle=self.data_cycle, airport_id=airport_id)

                    # Create the procedure
                    procedure, created = Procedure.objects.get_or_create(
                        cycle=self.data_cycle,
                        airport=airport,
                        procedure_id=procedure_id,
                        defaults={
                            "procedure_type": "STAR",
                        },
                    )

                    # Create the transition
                    transition_id = star_elem.find("TRANSITION_IDENTIFIER").text
                    transition, created = ProcedureTransition.objects.get_or_create(
                        procedure=procedure, transition_id=transition_id
                    )

                    # Create the leg
                    sequence_number = int(star_elem.find("SEQUENCE_NUMBER").text)
                    waypoint_identifier = star_elem.find("WAYPOINT_IDENTIFIER").text

                    leg, created = ProcedureLeg.objects.get_or_create(
                        transition=transition,
                        sequence_number=sequence_number,
                        defaults={
                            "waypoint_identifier": waypoint_identifier,
                            "waypoint_type": star_elem.find("WAYPOINT_TYPE").text,
                            "altitude_constraint": star_elem.find("ALTITUDE_CONSTRAINT").text
                            if star_elem.find("ALTITUDE_CONSTRAINT") is not None
                            else None,
                            "speed_constraint": star_elem.find("SPEED_CONSTRAINT").text
                            if star_elem.find("SPEED_CONSTRAINT") is not None
                            else None,
                        },
                    )
                except Airport.DoesNotExist:
                    self.logger.error(f"Airport with identifier {airport_id} not found!")
                self.logger.info("Parsing STARs finished")
