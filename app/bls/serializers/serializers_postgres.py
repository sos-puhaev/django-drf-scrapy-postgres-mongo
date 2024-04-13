from rest_framework import serializers
from ..models import PosgresDataModels

class PostgresDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = PosgresDataModels
        fields = '__all__'
