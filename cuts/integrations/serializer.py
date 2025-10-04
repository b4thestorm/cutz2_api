from rest_framework import serializers
from integrations.models import Booking

class BookingSerializer(serializers.Serializer):
    class Meta:
        model = Booking