from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required

from api.decorators import admin_required
from api.models import MedicalFacility, Patient


# @admin_required
def facility_list(request):
    facilities = MedicalFacility.objects.all()
    return render(request, 'facility_list.html', {'facilities': facilities, 'tab': 'facilities'})


# @admin_required
def user_list(request):
    users = User.objects.select_related('facility').all()
    return render(request, 'user_list.html', {'users': users, 'tab': 'users'})


# @admin_required
def patient_list(request):
    query = request.GET.get("q", "")
    if query:
        patients = Patient.objects.filter(name__icontains=query)
    else:
        patients = Patient.objects.all()
    return render(request, 'patient_list.html', {
        'patients': patients,
        'tab': 'patients',
        'query': query
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
