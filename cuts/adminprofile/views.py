import webbrowser
from django.conf import settings
from adminprofile.models import CustomUser, Services
from adminprofile.serializer import CustomUserSerializer, ServiceSerializer, LoginSerializer, PasswordSerializer, PasswordResetSerializer
from rest_framework import reverse, viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.decorators import api_view

from django.utils import encoding 
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.core.mail import send_mail

@api_view(['GET'])
def barber_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response(status=200)
    else:
        return Response(status=403, data="HTTP 403 Forbidden Response")

@api_view(['POST'])
def barber_login_view(request):
    serializer = LoginSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        email = serializer.validated_data.get("email", None)
        password = serializer.validated_data.get("password", None)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            serialized_user = CustomUserSerializer(user).data
            return Response(status=200, data=serialized_user)
        else:
            return Response(status=403, data="HTTP 403 Forbidden response")

@api_view(['POST'])
def send_password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        email = serializer.validated_data.get("email", None)
        try:
            customer = CustomUser.objects.get(email=email)
            base64_encoded_id = urlsafe_base64_encode(encoding.force_bytes(customer.id))
            token = PasswordResetTokenGenerator().make_token(customer)
            reset_url_args = {'pk': base64_encoded_id, 'token': token}
            reset_path = reverse.reverse('reset_password', kwargs=reset_url_args)
            reset_link = f'{settings.BASE_URL}{reset_path}'
            send_mail(
                "password reset link",
                f"""This <a href={reset_link}>Link</a> is only valid for the next 30 minutes.
                        If you didn't request a password reset, you can safely ignore this email. Your account is still secure.
                        If you have any questions, please contact our support team.
                        Thanks,
                        Arnold""",
                "arnoldsander@gmail.com",
                [customer.email],
                fail_silently=False,
            )
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def reset_password(request, pk, token):
    if request.method == 'GET':
          webbrowser.open(f"http://localhost:3000/reset-password/#{pk}/#{token}")
          return Response(status=status.HTTP_307_TEMPORARY_REDIRECT)
    elif request.method == 'POST':
          try:
            customer_id = int(urlsafe_base64_decode(pk))
            customer = CustomUser.objects.get(id=customer_id)
            serializer = PasswordSerializer(data=request.data, partial=True)
          except Exception as e:
              return Response(status=status.HTTP_400_BAD_REQUEST)
          if PasswordResetTokenGenerator().check_token(customer, token):
                if serializer.is_valid():
                    password = serializer.validated_data.get("password", None)
                    customer.set_password(password)
                    customer.save()
                    return Response(status=status.HTTP_200_OK, data="password reset successful")
                else:
                    Response(status=status.HTTP_401_UNAUTHORIZED)
          else:
             Response(status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_200_OK)
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    parser_classes =[JSONParser, MultiPartParser, FormParser]
    serializer_class = CustomUserSerializer
    
    @method_decorator(login_required())
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
    serializer_class = ServiceSerializer
    queryset = Services.objects.all()
    
    def create(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                barber = serializer.validated_data.get("barber", None)
            except Exception as e:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            title = serializer.validated_data.get("title", None)
            description = serializer.validated_data.get("description", None)
            image_url = serializer.validated_data.get("image_url", None)
            price = serializer.validated_data.get("price", None)
            service = Services(title=title, description=description, image_url=image_url, price=price, barber=barber)
            service.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            print("CHECK THIS OUT")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)