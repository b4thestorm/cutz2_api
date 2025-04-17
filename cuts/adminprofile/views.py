from adminprofile.models import CustomUser, Services
from adminprofile.serializer import CustomUserSerializer, ServiceSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
import pdb

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    parser_classes =[JSONParser, MultiPartParser, FormParser]
    serializer_class = CustomUserSerializer
    
    def patch(self, request, pk):
        instance = self.get_object(pk)
        serializer = CustomUserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201, data=serializer.data)
        return Response(status=400, data="wrong parameters")

    def create(self, request):
        data = request.data
        serializer = CustomUserSerializer(data=data, partial=True)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
             username =  serializer.validated_data.get("username", None),
             email = serializer.validated_data.get("email", None),
             first_name=serializer.validated_data.get("first_name", None),
             last_name=serializer.validated_data.get("last_name", None),
             role=CustomUser.Role.BARBER
            )
            user.set_password(serializer.validated_data.get("password", None))
            user.save()
        
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class ServiceViewSet(viewsets.ModelViewSet):
    def create(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                barber = serializer.validated_data.get("barber", None)
            except Exception as e:
                return Response(status=status.HTTP_404_NOT_FOUND)

            title = serializer.validated_data.get("title", None)
            description = serializer.validated_data.get("description", None)
            image_url =serializer.validated_data.get("image_url", None)
            price = serializer.validated_data.get("price", None)
            service = Services(title=title, description=description, image_url=image_url, price=price, barber=barber)
            service.save()
        
        return Response(status=status.HTTP_200_OK)
        