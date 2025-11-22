from rest_framework import serializers
from .models import EquipmentDataset
from django.contrib.auth.models import User

class EquipmentDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentDataset
        fields = '__all__'  # Include all fields from model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Only these fields
