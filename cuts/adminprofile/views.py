from django.shortcuts import render
from adminprofile.models import CustomUser
from adminprofile.serializer import CustomUserSerializer
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    def create(self, request):
        data = request.data
        serializer = CustomUserSerializer(data)
        if serializer.is_valid():
            payload = serializer.data
            user = CustomUser.create_user(
             email = payload.get("email", None),
             first_name=payload.get("first_name", None),
             last_name=payload.get("last_name", None),
             password=payload.get("password"),
             role=CustomUser.Role.BARBER
            )
            user.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)