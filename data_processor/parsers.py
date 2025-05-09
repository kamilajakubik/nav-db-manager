import logging
from xml.etree.ElementTree import Element

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

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
    """
    Parse ARINC 424 XML data into Django models.

    Attributes:
        data_cycle (DataCycle): The current data cycle to associate parsed objects with.
        logger (logging.Logger): Logger instance for logging parsing activities.
    """

    def __init__(self, data_cycle: DataCycle) -> None:
        self.data_cycle = data_cycle
        self.logger = logging.getLogger(__name__)

    def parse_file(self, root: Element) -> None:
        """
        Parse the ARINC 424 XML file within a DB transaction.

        Rolls back the whole parsing operation if any step fails.

        Args:
            root (Element): Root XML element of the file.
        """
        with transaction.atomic:
            try:
                self._parse_airports(root.find("AIRPORTS"))
                self._parse_navaids(root.find("NAVAIDS"))
                self._parse_waypoints(root.find("WAYPOINTS"))
                self._parse_airways(root.find("AIRWAYS"))
                self._parse_procedures(root.find("PROCEDURES"))
            except Exception as e:
                self.logger.error("Parsing failed — rolling back transaction.")
                raise  # Re-raise to trigger rollback

    def _get_text(self, parent: Element, tag: str) -> str | None:
        """Extract text from an XML element's child tag, if available."""
        element = parent.find(tag)
        return element.text.strip() if element is not None and element.text else None

    def _get_float(self, parent: Element, tag: str) -> str | None:
        """Extract a float from an XML tag, if available."""
        try:
            text = self._get_text(parent, tag)
            return float(text) if text is not None else None
        except ValueError:
            self.logger.warning(f"Invalid float value for tag '{tag}'")
            return None

    def _get_int(self, parent: Element, tag: str) -> str | None:
        """Extract an int from an XML tag, if available."""
        try:
            text = self._get_text(parent, tag)
            return int(text) if text is not None else None
        except ValueError:
            self.logger.warning(f"Invalid integer value for tag '{tag}'")
            return None

    def _parse_airports(self, airports_element: Element | None) -> None:
        if airports_element is None:
            self.logger.warning("No airports element found")
            return

        self.logger.info("Parsing airports...")
        for airport_elem in airports_element.findall("AIRPORT"):
            airport_id = self._get_text(airport_elem, "AIRPORT_IDENTIFIER")
            if not airport_id:
                continue

            try:
                Airport.objects.create(
                    cycle=self.data_cycle,
                    airport_id=airport_id,
                    defaults={
                        "icao_code": self._get_text(airport_elem, "ICAO_CODE"),
                        "name": self._get_text(airport_elem, "AIRPORT_NAME"),
                        "city": self._get_text(airport_elem, "CITY_NAME"),
                        "state": self._get_text(airport_elem, "STATE_CODE"),
                        "country": self._get_text(airport_elem, "COUNTRY_CODE"),
                        "latitude": self._get_float(airport_elem, ".//LATITUDE"),
                        "longitude": self._get_float(airport_elem, ".//LONGITUDE"),
                        "elevation": self._get_int(airport_elem, "ELEVATION"),
                        "magnetic_variation": self._get_text(airport_elem, "MAGNETIC_VARIATION"),
                        "transition_altitude": self._get_int(airport_elem, "TRANSITION_ALTITUDE"),
                        "transition_level": self._get_int(airport_elem, "TRANSITION_LEVEL"),
                        "longest_runway": self._get_int(airport_elem, "LONGEST_RUNWAY"),
                    },
                )
            except Exception as e:
                self.logger.error(f"Failed to parse airport '{airport_id}': {e}")
                raise Exception(f"{type(e).__name__} occurred during parsing: {e}")
        self.logger.info("Finished parsing airports")

    def _parse_navaids(self, navaids_element: Element | None) -> None:
        if navaids_element is None:
            self.logger.warning("No navaids element found")
            return

        self.logger.info("Parsing navaids...")
        for navaid_elem in navaids_element.findall("NAVAID"):
            navaid_id = self._get_text(navaid_elem, "NAVAID_IDENTIFIER")
            if not navaid_id:
                continue

            try:
                Navaid.objects.create(
                    cycle=self.data_cycle,
                    navaid_id=navaid_id,
                    defaults={
                        "name": self._get_text(navaid_elem, "NAVAID_NAME"),
                        "navaid_type": self._get_text(navaid_elem, "NAVAID_TYPE"),
                        "frequency": self._get_float(navaid_elem, "NAVAID_FREQUENCY"),
                        "latitude": self._get_float(navaid_elem, ".//LATITUDE"),
                        "longitude": self._get_float(navaid_elem, ".//LONGITUDE"),
                        "elevation": self._get_int(navaid_elem, "ELEVATION"),
                        "magnetic_variation": self._get_text(navaid_elem, "MAGNETIC_VARIATION"),
                        "dme_latitude": self._get_float(navaid_elem, ".//DME_POSITION/LATITUDE"),
                        "dme_longitude": self._get_float(navaid_elem, ".//DME_POSITION/LONGITUDE"),
                        "dme_elevation": self._get_int(navaid_elem, ".//DME_POSITION/ELEVATION"),
                        "service_volume": self._get_text(navaid_elem, "SERVICE_VOLUME"),
                    },
                )
            except Exception as e:
                self.logger.error(f"Failed to parse navaid '{navaid_id}': {e}")
                raise Exception(f"{type(e).__name__} occurred during parsing: {e}")
        self.logger.info("Finished parsing navaids")

    def _parse_waypoints(self, waypoints_element: Element | None) -> None:
        if waypoints_element is None:
            self.logger.warning("No waypoints element found")
            return

        self.logger.info("Parsing waypoints...")
        for waypoint_elem in waypoints_element.findall("WAYPOINT"):
            waypoint_id = self._get_text(waypoint_elem, "WAYPOINT_IDENTIFIER")
            if not waypoint_id:
                continue

            try:
                Waypoint.objects.create(
                    cycle=self.data_cycle,
                    waypoint_id=waypoint_id,
                    defaults={
                        "name": self._get_text(waypoint_elem, "WAYPOINT_NAME"),
                        "waypoint_type": self._get_text(waypoint_elem, "WAYPOINT_TYPE"),
                        "latitude": self._get_float(waypoint_elem, ".//LATITUDE"),
                        "longitude": self._get_float(waypoint_elem, ".//LONGITUDE"),
                        "airspace_classification": self._get_text(waypoint_elem, "AIRSPACE_CLASSIFICATION"),
                    },
                )
            except Exception as e:
                self.logger.error(f"Failed to parse waypoint '{waypoint_id}': {e}")
                raise Exception(f"{type(e).__name__} occurred during parsing: {e}")
        self.logger.info("Finished parsing waypoints")

    def _parse_airways(self, airways_element: Element | None) -> None:
        if airways_element is None:
            self.logger.warning("No airways element found")
            return

        self.logger.info("Parsing airways...")
        for airway_elem in airways_element.findall("AIRWAY"):
            airway_id = self._get_text(airway_elem, "ROUTE_IDENTIFIER")
            if not airway_id:
                continue

            try:
                airway = Airway.objects.create(
                    cycle=self.data_cycle,
                    airway_id=airway_id,
                    defaults={"route_type": self._get_text(airway_elem, "ROUTE_TYPE")},
                )

                sequence_number = self._get_int(airway_elem, "SEQUENCE_NUMBER")
                if sequence_number is not None:
                    AirwaySegment.objects.create(
                        airway=airway,
                        sequence_number=sequence_number,
                        defaults={
                            "fix_identifier": self._get_text(airway_elem, "FIX_IDENTIFIER"),
                            "fix_type": self._get_text(airway_elem, "FIX_TYPE"),
                            "next_fix_identifier": self._get_text(airway_elem, "NEXT_FIX_IDENTIFIER"),
                            "next_fix_type": self._get_text(airway_elem, "NEXT_FIX_TYPE"),
                            "route_distance": self._get_int(airway_elem, "ROUTE_DISTANCE"),
                            "minimum_altitude": self._get_int(airway_elem, "MINIMUM_ALTITUDE"),
                            "maximum_altitude": self._get_int(airway_elem, "MAXIMUM_ALTITUDE"),
                            "magnetic_course": self._get_int(airway_elem, "MAGNETIC_COURSE"),
                            "reverse_magnetic_course": self._get_int(airway_elem, "REVERSE_MAGNETIC_COURSE"),
                        },
                    )
            except Exception as e:
                self.logger.error(f"Failed to parse airway '{airway_id}': {e}")
                raise Exception(f"{type(e).__name__} occurred during parsing: {e}")
        self.logger.info("Finished parsing airways")

    def _parse_procedures(self, procedures_element: Element | None) -> None:
        if procedures_element is None:
            self.logger.warning("No procedures element found")
            return

        self._parse_procedure_type(procedures_element, "APPROACH")
        self._parse_procedure_type(procedures_element, "SID")
        self._parse_procedure_type(procedures_element, "STAR")

    def _parse_procedure_type(self, parent_element: Element, tag_name: str) -> None:
        """Parse procedures of a specific type: APPROACH, SID, STAR."""
        self.logger.info(f"Parsing {tag_name}s...")
        for proc_elem in parent_element.findall(tag_name):
            airport_id = self._get_text(proc_elem, "AIRPORT_IDENTIFIER")
            procedure_id = self._get_text(proc_elem, "PROCEDURE_IDENTIFIER")
            if not airport_id or not procedure_id:
                continue

            try:
                airport = Airport.objects.get(cycle=self.data_cycle, airport_id=airport_id)

                procedure = Procedure.objects.create(
                    cycle=self.data_cycle,
                    airport=airport,
                    procedure_id=procedure_id,
                    defaults={"procedure_type": tag_name},
                )

                transition_id = self._get_text(proc_elem, "TRANSITION_IDENTIFIER")
                transition = ProcedureTransition.objects.create(procedure=procedure, transition_id=transition_id)

                sequence_number = self._get_int(proc_elem, "SEQUENCE_NUMBER")
                waypoint_identifier = self._get_text(proc_elem, "WAYPOINT_IDENTIFIER")

                if sequence_number is not None and waypoint_identifier:
                    ProcedureLeg.objects.create(
                        transition=transition,
                        sequence_number=sequence_number,
                        defaults={
                            "waypoint_identifier": waypoint_identifier,
                            "waypoint_type": self._get_text(proc_elem, "WAYPOINT_TYPE"),
                            "latitude": self._get_float(proc_elem, ".//POSITION/LATITUDE"),
                            "longitude": self._get_float(proc_elem, ".//POSITION/LONGITUDE"),
                            "altitude_constraint": self._get_text(proc_elem, "ALTITUDE_CONSTRAINT"),
                            "speed_constraint": self._get_text(proc_elem, "SPEED_CONSTRAINT"),
                            "course": self._get_int(proc_elem, "COURSE"),
                            "distance": self._get_float(proc_elem, "DISTANCE"),
                        },
                    )
            except ObjectDoesNotExist:
                self.logger.error(f"{tag_name}: Airport '{airport_id}' not found.")
            except Exception as e:
                self.logger.error(f"Failed to parse {tag_name} for airport '{airport_id}': {e}")
                raise Exception(f"{type(e).__name__} occurred during parsing: {e}")
        self.logger.info(f"Finished parsing {tag_name}s")
