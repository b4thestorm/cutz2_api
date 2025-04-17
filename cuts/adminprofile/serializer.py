from rest_framework import serializers
from .models import CustomUser, Services

class CustomUserSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(max_length=None, use_url=True, required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=None, required=False)
    password = serializers.CharField(max_length=None, required=False)
    description = serializers.CharField(max_length=None, required=False)
    street_address = serializers.CharField(max_length=None, required=False)
    city = serializers.CharField(max_length=None, required=False)
    state = serializers.CharField(max_length=None, required=False)
    zip_code = serializers.CharField(max_length=None, required=False)
    class Meta:
        model = CustomUser
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = Services
        fields = '__all__'

