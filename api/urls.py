from django.urls import path
from .views import *

urlpatterns = [
    path('', lambda request: redirect('login'), name='root_redirect'),
    path('facilities/', facility_list, name='facility_list'),
    path('users/', user_list, name='user_list'),
    path('patients/', patient_list, name='patient_list'),
    path('dashboard/', dashboard, name='dashboard'),
    path('diagnosis/', diagnosis_list, name='diagnosis_list'),

    path('api/facilities/create/', create_facility, name='create_facility'),
    path('api/facilities/update/<int:pk>/', update_facility, name='update_facility'),
    path('api/facilities/delete/<int:pk>/', delete_facility, name='delete_facility'),

    path('api/users/create/', create_user),
    path('api/users/update/<int:pk>/', update_user),
    path('api/users/delete/<int:pk>/', delete_user),

    path('api/patients/<int:pk>/', get_patient),
    path('api/patients/create/', create_patient),
    path('api/patients/update/<int:pk>/', update_patient),
    path('api/patients/delete/<int:pk>/', delete_patient),

    path('api/diagnosis/create/', create_diagnosis, name='create_diagnosis'),
    path('api/diagnosis/update/<int:id>/', update_diagnosis, name='update_diagnosis'),
    path('api/diagnosis/delete/<int:id>/', delete_diagnosis, name='delete_diagnosis'),
    path('api/diagnosis/<int:id>/', get_diagnosis, name='get_diagnosis'),
    path('api/diagnosis/list/', diagnosis_list_api, name='diagnosis_list_api'),

    path('api/get_doctors_by_patient/<int:patient_id>/', get_doctors_by_patient, name='get_doctors_by_patient'),
    path('diagnosis_report/', diagnosis_report, name='diagnosis_report'),

    path('api/diagnosis/generate_public_link/<int:id>/', generate_public_link, name='generate_public_link'),
    path('diagnosis/public/<str:token>/', diagnosis_public_view, name='diagnosis_public_view'),

]
