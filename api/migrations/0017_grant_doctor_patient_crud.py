from django.db import migrations


def grant_doctor_patient_crud(apps, schema_editor):
    Role = apps.get_model('api', 'Role')
    Permission = apps.get_model('api', 'Permission')

    try:
        doctor_role = Role.objects.get(code='doctor')
    except Role.DoesNotExist:
        return

    patient_permissions = Permission.objects.filter(
        code__in=[
            'patient.view',
            'patient.create',
            'patient.edit',
            'patient.delete',
        ]
    )
    doctor_role.permissions.add(*patient_permissions)


def revoke_doctor_patient_crud(apps, schema_editor):
    Role = apps.get_model('api', 'Role')
    Permission = apps.get_model('api', 'Permission')

    try:
        doctor_role = Role.objects.get(code='doctor')
    except Role.DoesNotExist:
        return

    patient_permissions = Permission.objects.filter(
        code__in=[
            'patient.create',
            'patient.edit',
            'patient.delete',
        ]
    )
    doctor_role.permissions.remove(*patient_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_user_patient_link'),
    ]

    operations = [
        migrations.RunPython(grant_doctor_patient_crud, revoke_doctor_patient_crud),
    ]
