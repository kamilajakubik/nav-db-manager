from decimal import Decimal

import pytest
import logging

from model_bakery import baker

from data_processor.tests.test_data import valid_airport_xml, invalid_airport_xml
from navigation.models import Airport, Navaid, Waypoint, Airway, AirwaySegment, Procedure, ProcedureLeg, DataCycle
from data_processor.parsers import ARINCParser


@pytest.fixture
def cycle():
    return baker.make("DataCycle")


@pytest.fixture
def parser(cycle):
    return ARINCParser(data_cycle=cycle)


@pytest.mark.django_db
class TestAirportParser:
    def test_parse_airports_success(self, parser, cycle):
        parser._parse_airports(valid_airport_xml)
        airport = Airport.objects.filter(cycle=cycle).get(airport_id="KJFK")
        assert airport.icao_code == "KJFK"
        assert airport.latitude == Decimal("40.639751")
        assert airport.longitude == Decimal("-73.778925")

    def test_parse_missing_airport_tag(self, parser, caplog):
        caplog.set_level(logging.WARNING)
        parser._parse_airports(None)
        assert "No airports element found" in caplog.text

    def test_parse_airport_invalid_float(self, parser, caplog):
        with pytest.raises(Exception):
            parser._parse_airports(invalid_airport_xml)
        assert "Invalid float value" in caplog.text


@pytest.mark.django_db
class TestFileParser:
    def test_parse_file_rolls_back_on_error(self, parser, mocker, caplog):
        mocker.patch.object(parser, "_parse_navaids", side_effect=Exception("Boom"))
        with pytest.raises(Exception, match="Boom"):
            parser.parse_file(invalid_airport_xml)
        assert Airport.objects.count() == 0
        assert "Parsing failed — rolling back transaction." in caplog.text
