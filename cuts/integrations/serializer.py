from rest_framework import serializers
from adminprofile.serializer import CustomUserSerializer, ServiceSerializer
from integrations.models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['eventid', 'start_time', 'end_time', 'service_id']
        depth = 1