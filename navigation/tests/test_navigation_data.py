import pytest
from model_bakery import baker
from rest_framework import status
from ..serializers import AirportSerializer


@pytest.fixture
def cycle():
    return baker.make("DataCycle")

@pytest.fixture
def airport(cycle):
    return baker.make("Airport", cycle=cycle)

@pytest.fixture
def airport_with_procedures(cycle):
    airport = baker.make("Airport", cycle=cycle)
    baker.make("Procedure", cycle=cycle, airport=airport)
    return airport


@pytest.mark.django_db
class TestRetrieveNavigationData:
    def test_if_airport_exists_returns_200(self, api_client, airport):
        response = api_client.get(f"/navigation/airports/{airport.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == AirportSerializer(airport).data

    def test_if_airport_procedure_exists_returns_200(self, api_client, airport_with_procedures):
        response = api_client.get(f"/navigation/airports/{airport_with_procedures.id}/procedures/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_if_airport_procedure_not_exists_returns_404(self, api_client, airport):
        response = api_client.get(f"/navigation/airports/{airport.id}/procedures/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No procedures found for this airport."