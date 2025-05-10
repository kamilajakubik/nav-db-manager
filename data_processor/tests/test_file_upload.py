import io

import pytest
from django.urls import reverse
from rest_framework import status

from data_processor.models import ArincFile


@pytest.mark.django_db
class TestFileUpload:
    def test_file_upload_returns_201(self, api_client, mocker):
        mock_task = mocker.patch("data_processor.tasks.process_arinc_file.delay")

        file_content = b"<dummy>content<dummy>"
        test_file = io.BytesIO(file_content)
        test_file.name = "test.xml"

        url = reverse("upload-list")
        response = api_client.post(url, {"file": test_file}, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert ArincFile.objects.count() == 1

        arinc_file = ArincFile.objects.first()
        assert response.data["id"] == arinc_file.id
        mock_task.assert_called_once_with(arinc_file.id)
