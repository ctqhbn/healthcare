from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from api.decorators import admin_required
from api.models import MedicalFacility, Patient, PatientDocument
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.hashers import make_password

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
        return render(request, 'facility_list.html')
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
