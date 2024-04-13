from rest_framework import generics
from ..models import PosgresDataModels
from rest_framework.response import Response
from rest_framework import status
from ..serializers.serializers_postgres import PostgresDataSerializers
from rest_framework.permissions import IsAuthenticated
import logging

class PosgresDataListCreateView(generics.ListCreateAPIView):
    queryset = PosgresDataModels.objects.all()
    serializer_class = PostgresDataSerializers
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        torrent_value = request.query_params.get('id_torrent', None)

        if not torrent_value:
            return Response({'error': 'Missing id_torrent parameter'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = PosgresDataModels.objects.filter(id_torrent=torrent_value).values('name', 'email', 'data_comment', 'comments', 'audio', 'video')

        if not queryset.exists():
            return Response({'error': 'No data found for the given magnet value'}, status=status.HTTP_404_NOT_FOUND)

        return Response(queryset)