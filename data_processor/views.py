from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import ArincFile
from .serializers import ArincFileSerializer
from .tasks import process_arinc_file


class FileViewSet(ModelViewSet):
    queryset = ArincFile.objects.all()
    serializer_class = ArincFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = ArincFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        arinc_file = serializer.save()
        process_arinc_file.delay(arinc_file.id)
        serializer = ArincFileSerializer(arinc_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

