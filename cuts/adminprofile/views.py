from django.shortcuts import render
from cuts.adminprofile.models import CustomUser
from rest_framework import permissions, viewsets


class UserViewSet(viewsets.ModelViewSet):
    def create(self, request):
        pass