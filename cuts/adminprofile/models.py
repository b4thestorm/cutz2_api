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
    class Role(models.TextChoices):
        BARBER = "BARBER", 'Barber'
        CLIENT = "CLIENT", 'Client'
    
    email = models.EmailField(_("email address"), unique=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    image_url = models.ImageField(null=True, blank=True, upload_to='images/')
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.BARBER)
    
    base_role = Role.BARBER

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)

class Barber(CustomUser):
    base_role = CustomUser.Role.BARBER
    class Meta:
        proxy = True

class Client(CustomUser):
    base_role = CustomUser.Role.CLIENT
    class Meta:
        proxy = True

class Services(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    image_url = models.ImageField(null=True, blank=True, upload_to='images/')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    barber = models.ForeignKey(CustomUser, on_delete=models.CASCADE)