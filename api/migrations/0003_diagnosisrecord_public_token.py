# Generated by Django 4.1.3 on 2025-06-08 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_diagnosisrecord_facility_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosisrecord',
            name='public_token',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
