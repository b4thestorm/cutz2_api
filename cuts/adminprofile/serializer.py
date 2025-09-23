from django.db import models
from rest_framework import serializers
from .models import CustomUser, Services

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=True)
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

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

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['password']