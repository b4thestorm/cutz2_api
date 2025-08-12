from django.db import models
from adminprofile.models import Barber

class GCalIntegration(models.Model):
    user = models.ForeignKey(Barber, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, null=True)
    access_token = models.CharField(max_length=255)
    expiration_time = models.IntegerField(default=0)