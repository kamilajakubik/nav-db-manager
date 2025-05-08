from rest_framework import serializers

from .models import ArincFile


class ArincFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArincFile
        fields = [
            "id",
            "file",
            "uploaded_at",
            "status",
            "cycle",
            "processing_errors",
        ]
        read_only_fields = [
            "uploaded_at",
            "status",
            "cycle",
            "processing_errors",
        ]
