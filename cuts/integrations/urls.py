from django.urls import path, include
import django_eventstream

from . import views

urlpatterns = [
    path("gcal_init/", views.gcal_init, name="gcal_init"),
    path("gcal_auth", views.gcal_auth, name="gcal_auth"),
    path("calendar_events/", views.calendar_events, name="calendar_events"),
    path("test/", views.test_stream, name="test"),
    path("events/", include(django_eventstream.urls), {"channels": ["gcal_init"]}),
]