from django.urls import path
from . import views

urlpatterns = [
    path("barber_agent/", views.barber_agent, name="barber_agent"),
]