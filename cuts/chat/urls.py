from django.urls import path
from . import views

urlpatterns = [
    path("agent/", views.barber_agent, name="barber_agent"),
]