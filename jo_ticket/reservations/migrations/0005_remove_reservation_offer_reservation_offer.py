# Generated by Django 5.1.1 on 2024-10-08 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0004_reservation_qr_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reservation",
            name="offer",
        ),
        migrations.AddField(
            model_name="reservation",
            name="offer",
            field=models.ManyToManyField(to="reservations.offer"),
        ),
    ]
