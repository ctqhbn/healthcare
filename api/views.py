from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from api.decorators import admin_required
from api.models import DiagnosisDocument, DiagnosisRecord, MedicalFacility, Patient, PatientDocument
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_GET
from django.db.models import Count
from django.utils.dateparse import parse_date

from datetime import datetime

import json


@admin_required
def facility_list(request):
    facilities = MedicalFacility.objects.all()
    return render(request, 'facility_list.html', {'facilities': facilities, 'tab': 'facilities'})


@admin_required
def user_list(request):
    users = User.objects.select_related('facility').all()
    facilities = MedicalFacility.objects.all()
    return render(request, 'user_list.html', {'users': users, 'tab': 'users', 'facilities': facilities})


@admin_required
def patient_list(request):
    patients = Patient.objects.all()
    facilities = MedicalFacility.objects.all()
    return render(request, 'patient_list.html', {
        'patients': patients,
        'tab': 'patients',
        'facilities': facilities,
    })


@login_required
def dashboard(request):
    print(request.user.role, "ROLE")
    if request.user.role == 'admin':
        return redirect('facility_list')
    elif request.user.role == 'doctor':
        return redirect('diagnosis_list')
    else:
        return redirect('logout')  # hoặc trang lỗi


@csrf_exempt
def create_facility(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            facility = MedicalFacility.objects.create(
                code=data['code'],
                name=data['name'],
                address=data['address']
            )
            return JsonResponse({'message': 'Tạo thành công', 'id': facility.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def update_facility(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            facility = MedicalFacility.objects.get(pk=pk)
            facility.code = data['code']
            facility.name = data['name']
            facility.address = data['address']
            facility.save()
            return JsonResponse({'message': 'Cập nhật thành công'})
        except MedicalFacility.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def delete_facility(request, pk):
    if request.method == 'POST':
        try:
            facility = MedicalFacility.objects.get(pk=pk)
            facility.delete()
            return JsonResponse({'message': 'Đã xóa thành công'})
        except MedicalFacility.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy'}, status=404)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User(
                code=data['code'],
                username=data['username'],
                name=data['name'],
                role=data['role'],
                facility=MedicalFacility.objects.get(pk=data['facility']) if data.get('facility') else None,
                password=make_password(data['password'])  # hash mật khẩu
            )
            user.save()
            return JsonResponse({'message': 'Tạo người dùng thành công', 'id': user.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def update_user(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.get(pk=pk)
            user.code = data['code']
            user.username = data['username']
            user.name = data['name']
            user.role = data['role']
            user.facility = MedicalFacility.objects.get(pk=data['facility']) if data.get('facility') else None
            # Nếu có password mới thì cập nhật (hash password)
            if data.get('password'):
                user.password = make_password(data['password'])
            user.save()
            return JsonResponse({'message': 'Cập nhật người dùng thành công'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy người dùng'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def delete_user(request, pk):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return JsonResponse({'message': 'Đã xóa thành công'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy người dùng'}, status=404)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def create_patient(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                identifier_type = request.POST['identifier_type']
                identifier = request.POST['identifier']
                name = request.POST['name']
                contact_info = request.POST.get('contact_info')
                gender = request.POST['gender']
                facility_id = request.POST.get('facility_id')

                patient = Patient.objects.create(
                    identifier_type=identifier_type,
                    identifier=identifier,
                    name=name,
                    contact_info=contact_info,
                    gender=gender,
                    created_by_facility_id=facility_id if facility_id else None
                )

                for file in request.FILES.getlist('documents'):
                    PatientDocument.objects.create(patient=patient, file=file, original_filename=file.name)

                return JsonResponse({'message': 'Tạo bệnh nhân thành công', 'id': patient.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def update_patient(request, pk):
    if request.method == 'POST':
        try:
            patient = Patient.objects.get(pk=pk)

            patient.identifier_type = request.POST['identifier_type']
            patient.identifier = request.POST['identifier']
            patient.name = request.POST['name']
            patient.contact_info = request.POST.get('contact_info')
            patient.gender = request.POST['gender']
            patient.created_by_facility_id = request.POST.get('facility_id') or None
            patient.save()

            for file in request.FILES.getlist('documents'):
                PatientDocument.objects.create(patient=patient, file=file, original_filename=file.name)
            delete_docs_ids = request.POST.get('delete_documents', '')
            if delete_docs_ids:
                delete_ids = [int(i) for i in delete_docs_ids.split(',') if i.strip().isdigit()]
                PatientDocument.objects.filter(id__in=delete_ids, patient=patient).delete()

            return JsonResponse({'message': 'Cập nhật thành công'})
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy bệnh nhân'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def delete_patient(request, pk):
    if request.method == 'POST':
        try:
            patient = Patient.objects.get(pk=pk)
            patient.delete()
            return JsonResponse({'message': 'Xóa thành công'})
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy bệnh nhân'}, status=404)
    return HttpResponseBadRequest("Invalid method")


@csrf_exempt
def get_patient(request, pk):
    if request.method == 'GET':
        try:
            patient = Patient.objects.get(pk=pk)
            data = {
                'id': patient.id,
                'identifier_type': patient.identifier_type,
                'identifier': patient.identifier,
                'name': patient.name,
                'contact_info': patient.contact_info,
                'gender': patient.gender,
                'created_by_facility': patient.created_by_facility.id if patient.created_by_facility else None,
                'documents': [{"file_url": doc.file.url, "id": doc.id, "file_name": doc.original_filename} for doc in patient.documents.all()]
            }
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy bệnh nhân'}, status=404)

    return HttpResponseBadRequest("Invalid method")


def diagnosis_list(request):
    diagnosis_records = DiagnosisRecord.objects.all().select_related('doctor')
    facilities = MedicalFacility.objects.all()
    doctors = User.objects.filter(role='doctor')
    patients = Patient.objects.all()
    return render(request, 'diagnosis_list.html', {
        'diagnosis_records': diagnosis_records,
        'facilities': facilities,
        'doctors': doctors,
        'patients': patients,
        'tab': 'diagnosis'
    })


@csrf_exempt
@transaction.atomic
def create_diagnosis(request):
    if request.method == 'POST':
        try:
            patient_id = request.POST['patient_id']
            service_type = request.POST['service_type']
            department = request.POST['department']
            examination_place = request.POST['examination_place']
            examination_time = request.POST['examination_time']
            diagnosis_result = request.POST['diagnosis_result']
            doctor_id = request.POST.get('doctor_id')

            diagnosis = DiagnosisRecord.objects.create(
                patient=Patient.objects.get(id=patient_id),
                service_type=service_type,
                department=department,
                examination_place=examination_place,
                examination_time=examination_time,
                diagnosis_result=diagnosis_result,
                doctor=User.objects.get(pk=doctor_id) if doctor_id else None
            )

            for file in request.FILES.getlist('documents'):
                DiagnosisDocument.objects.create(diagnosis_record=diagnosis, file=file)

            return JsonResponse({'message': 'Tạo chuẩn đoán thành công', 'id': diagnosis.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@transaction.atomic
def update_diagnosis(request, id):
    if request.method == 'POST':
        try:
            diagnosis = DiagnosisRecord.objects.get(id=id)

            diagnosis.patient = Patient.objects.get(pk=request.POST['patient_id'])
            diagnosis.service_type = request.POST['service_type']
            diagnosis.department = request.POST['department']
            diagnosis.examination_place = request.POST['examination_place']
            diagnosis.examination_time = request.POST['examination_time']
            diagnosis.diagnosis_result = request.POST['diagnosis_result']
            doctor_id = request.POST.get('doctor_id')
            diagnosis.doctor = User.objects.get(pk=doctor_id) if doctor_id else None
            diagnosis.save()

            # Xóa file nếu user yêu cầu
            file_delete_list = json.loads(request.POST.get('files_to_delete', '[]'))
            DiagnosisDocument.objects.filter(id__in=file_delete_list, diagnosis_record=diagnosis).delete()

            # Thêm file mới
            for file in request.FILES.getlist('documents'):
                DiagnosisDocument.objects.create(diagnosis_record=diagnosis, file=file)

            return JsonResponse({'message': 'Cập nhật chuẩn đoán thành công'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def delete_diagnosis(request, id):
    if request.method == 'POST':
        try:
            diagnosis = DiagnosisRecord.objects.get(id=id)
            diagnosis.delete()
            return JsonResponse({'message': 'Xóa chuẩn đoán thành công'})
        except DiagnosisRecord.DoesNotExist:
            return JsonResponse({'error': 'Không tìm thấy chuẩn đoán'}, status=404)


def get_diagnosis(request, id):
    try:
        diagnosis = DiagnosisRecord.objects.get(id=id)
        documents = diagnosis.documents.all()

        documents_data = [
            {
                'id': doc.id,
                'file_url': doc.file.url,
                'file_name': doc.file.name.split('/')[-1]
            } for doc in documents
        ]

        data = {
            'id': diagnosis.id,
            'patient_id': diagnosis.patient.id,
            'service_type': diagnosis.service_type,
            'department': diagnosis.department,
            'examination_place': diagnosis.examination_place,
            'patient_name': diagnosis.patient.name,
            'examination_time': diagnosis.examination_time.isoformat(),
            'diagnosis_result': diagnosis.diagnosis_result,
            'doctor_id': diagnosis.doctor.id if diagnosis.doctor else '',
            'documents': documents_data
        }

        return JsonResponse(data)
    except DiagnosisRecord.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy chuẩn đoán'}, status=404)


@csrf_exempt
def diagnosis_list_api(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        identifier_number = request.GET.get('identifier_number')

        diagnoses = DiagnosisRecord.objects.all()

        if start_date:
            diagnoses = diagnoses.filter(examination_time__date__gte=start_date)
        if end_date:
            diagnoses = diagnoses.filter(examination_time__date__lte=end_date)
        if identifier_number:
            diagnoses = diagnoses.filter(patient__identifier__icontains=identifier_number)

        result = []
        for d in diagnoses:
            result.append({
                'id': d.id,
                'examination_time': d.examination_time.strftime("%Y-%m-%d %H:%M"),
                'patient_code': d.patient.id,
                'service_type': d.service_type,
                'facility_code': d.patient.created_by_facility.name,
                'department': d.department,
                'examination_place': d.examination_place,
                'identifier_number': d.patient.identifier,
                'patient_name': d.patient.name,
                'doctor_name': d.doctor.name if d.doctor else '',
            })

        return JsonResponse({'data': result}, safe=False)


@require_GET
def get_doctors_by_patient(request, patient_id):
    try:
        patient = Patient.objects.get(pk=patient_id)
        facility = patient.created_by_facility

        doctors = User.objects.filter(role='doctor', facility=facility)
        doctor_list = [
            {'id': d.id, 'name': d.name}
            for d in doctors
        ]

        return JsonResponse({'doctors': doctor_list})
    except Patient.DoesNotExist:
        return JsonResponse({'doctors': []})


def add_month(dt):
    year = dt.year + (dt.month // 12)
    month = dt.month % 12 + 1
    return datetime(year, month, 1)


def diagnosis_report(request):
    start_month = request.GET.get('start_month')
    end_month = request.GET.get('end_month')

    if not start_month or not end_month:
        today = datetime.today()
        start_month = end_month = today.strftime('%Y-%m')

    start_date = datetime.strptime(start_month, '%Y-%m').replace(day=1)
    end_dt = datetime.strptime(end_month, '%Y-%m')
    end_date = add_month(end_dt)

    records = DiagnosisRecord.objects.filter(
        examination_time__gte=start_date,
        examination_time__lt=end_date
    )

    # Group theo bệnh viện
    from django.db.models import Count

    facility_stats = records.values(
        'patient__created_by_facility__id',
        'patient__created_by_facility__name'
    ).annotate(
        total_patients=Count('patient', distinct=True),
        total_service_types=Count('service_type', distinct=True)
    ).order_by('patient__created_by_facility__name')

    context = {
        'facility_stats': facility_stats,
        'start_month': start_month,
        'end_month': end_month,
        'tab': 'diagnosis_report'
    }

    return render(request, 'diagnosis_report.html', context)
