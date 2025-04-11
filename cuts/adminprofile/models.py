from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class AddressMixin(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)

    class Meta:
        abstract = True

class CustomUser(AbstractUser, AddressMixin):
    email = models.EmailField(_("email address"), unique=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email