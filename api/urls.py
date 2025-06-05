from django.urls import path
from .views import *

urlpatterns = [
    path('facilities/', facility_list, name='facility_list'),
    path('users/', user_list, name='user_list'),
    path('patients/', patient_list, name='patient_list'),
    path('dashboard/', dashboard, name='dashboard'),

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
]
