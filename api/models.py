from django.db import models
from django.contrib.auth.models import AbstractUser

from healthcare import settings
import uuid

# Create your models here.

class MedicalFacility(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
    )
    code = models.CharField(max_length=50, unique=True)
    facility = models.ForeignKey(MedicalFacility, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class PatientDocument(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to='patient_documents/')
    original_filename = models.CharField(max_length=255, blank=True, null=True)  # thêm trường này
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.patient.name}"


class Patient(models.Model):
    IDENTIFIER_CHOICES = [
        ('insurance', 'Insurance Number'),
        ('national_id', 'National ID'),
        ('phone', 'Phone Number'),
    ]

    identifier_type = models.CharField(max_length=20, choices=IDENTIFIER_CHOICES)
    identifier = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    created_by_facility = models.ForeignKey(MedicalFacility, on_delete=models.SET_NULL, null=True, related_name="patients")
    activity_history = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name



class DiagnosisCatalog(models.Model):
    order_number = models.IntegerField()
    exam_time = models.DateTimeField()
    patient_code = models.CharField(max_length=100)
    patient_name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=255)
    facility = models.ForeignKey(MedicalFacility, on_delete=models.CASCADE, related_name="diagnoses")
    department = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    identifier = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.patient_name} - {self.exam_time.date()}"


class DiagnosisDetail(models.Model):
    diagnosis = models.ForeignKey(DiagnosisCatalog, on_delete=models.CASCADE, related_name="details")
    attachments = models.FileField(upload_to='diagnosis_attachments/', blank=True, null=True)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    result = models.TextField()

    def __str__(self):
        return f"Diagnosis by {self.doctor}"


class DiagnosisRecord(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='diagnosis_records')
    service_type = models.CharField(max_length=200)  # loại dịch vụ
    department = models.CharField(max_length=200)    # khoa
    examination_place = models.CharField(max_length=200)  # nơi khám
    examination_time = models.DateTimeField()        # thời gian khám
    public_token = models.CharField(max_length=100, null=True, blank=True, unique=True)

    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'doctor'},  # chỉ cho chọn user có role doctor
        related_name='diagnosis_records'
    )

    diagnosis_result = models.TextField()  # kết quả chuẩn đoán
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_public_token(self):
        self.public_token = uuid.uuid4().hex
        self.save()

    def __str__(self):
        return f'Chuẩn đoán {self.patient_code} - {self.patient_name} ({self.examination_time.date()})'


class DiagnosisDocument(models.Model):
    diagnosis_record = models.ForeignKey(
        DiagnosisRecord,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file = models.FileField(upload_to='diagnosis_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Document for {self.diagnosis_record.patient_code} - {self.file.name.split("/")[-1]}'