from rest_framework import serializers
from .models import CustomUser, Services

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
    

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = Services
        fields = '__all__'

