# Generated by Django 4.2 on 2025-04-16 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("adminprofile", "0005_alter_services_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="image_url",
            field=models.ImageField(blank=True, null=True, upload_to="images/"),
        ),
    ]
