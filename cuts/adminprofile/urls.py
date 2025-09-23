from .views import UserViewSet, ServiceViewSet, barber_login_view, barber_logout_view, send_password_reset, reset_password
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'services', ServiceViewSet, basename='services')

urlpatterns = router.urls
urlpatterns += [
    path(r'login', barber_login_view, name="login"),
    path(r'logout', barber_logout_view, name="logout"),
    path(r'send-reset-link', send_password_reset, name="reset_link"),
    path(r'reset-password/<pk>/<token>/', reset_password, name='reset_password')
]