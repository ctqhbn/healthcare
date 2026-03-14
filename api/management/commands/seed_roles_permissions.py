from django.core.management.base import BaseCommand
from api.models import Role, Permission


PERMISSIONS_DATA = [
    # User
    {'code': 'user.view', 'name': 'Xem người dùng', 'module': 'user'},
    {'code': 'user.create', 'name': 'Tạo người dùng', 'module': 'user'},
    {'code': 'user.edit', 'name': 'Sửa người dùng', 'module': 'user'},
    {'code': 'user.delete', 'name': 'Xóa người dùng', 'module': 'user'},
    # Facility
    {'code': 'facility.view', 'name': 'Xem cơ sở y tế', 'module': 'facility'},
    {'code': 'facility.create', 'name': 'Tạo cơ sở y tế', 'module': 'facility'},
    {'code': 'facility.edit', 'name': 'Sửa cơ sở y tế', 'module': 'facility'},
    {'code': 'facility.delete', 'name': 'Xóa cơ sở y tế', 'module': 'facility'},
    # Patient
    {'code': 'patient.view', 'name': 'Xem bệnh nhân', 'module': 'patient'},
    {'code': 'patient.create', 'name': 'Tạo bệnh nhân', 'module': 'patient'},
    {'code': 'patient.edit', 'name': 'Sửa bệnh nhân', 'module': 'patient'},
    {'code': 'patient.delete', 'name': 'Xóa bệnh nhân', 'module': 'patient'},
    # Diagnosis
    {'code': 'diagnosis.view', 'name': 'Xem chuẩn đoán', 'module': 'diagnosis'},
    {'code': 'diagnosis.create', 'name': 'Tạo chuẩn đoán', 'module': 'diagnosis'},
    {'code': 'diagnosis.edit', 'name': 'Sửa chuẩn đoán', 'module': 'diagnosis'},
    {'code': 'diagnosis.delete', 'name': 'Xóa chuẩn đoán', 'module': 'diagnosis'},
]

ROLES_DATA = [
    {
        'code': 'admin',
        'name': 'Quản trị viên',
        'description': 'Toàn quyền quản lý hệ thống',
        'permissions': '__all__',
    },
    {
        'code': 'doctor',
        'name': 'Bác sĩ',
        'description': 'Quản lý chuẩn đoán và xem bệnh nhân',
        'permissions': [
            'patient.view',
            'diagnosis.view', 'diagnosis.create', 'diagnosis.edit', 'diagnosis.delete',
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed default roles and permissions'

    def handle(self, *args, **options):
        # Create permissions
        created_perms = 0
        for pdata in PERMISSIONS_DATA:
            _, created = Permission.objects.get_or_create(
                code=pdata['code'],
                defaults={'name': pdata['name'], 'module': pdata['module']}
            )
            if created:
                created_perms += 1

        self.stdout.write(f'Permissions: {created_perms} created, {len(PERMISSIONS_DATA) - created_perms} already existed')

        # Create roles
        for rdata in ROLES_DATA:
            role, created = Role.objects.get_or_create(
                code=rdata['code'],
                defaults={'name': rdata['name'], 'description': rdata['description']}
            )

            if rdata['permissions'] == '__all__':
                role.permissions.set(Permission.objects.all())
            else:
                perm_objs = Permission.objects.filter(code__in=rdata['permissions'])
                role.permissions.set(perm_objs)

            status = 'created' if created else 'updated permissions'
            self.stdout.write(f'Role "{role.name}" ({role.code}): {status}')

        self.stdout.write(self.style.SUCCESS('Seed completed!'))
