from rest_framework import serializers
from integrations.models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['eventid','name', 'start_time', 'end_time', 'service_id']
        depth = 1