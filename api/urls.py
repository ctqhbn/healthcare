from django.urls import path
from .views import (
    facility_list,
    user_list,
    patient_list,
    dashboard
)


urlpatterns = [
    path('facilities/', facility_list, name='facility_list'),
    path('users/', user_list, name='user_list'),
    path('patients/', patient_list, name='patient_list'),
    path('dashboard/', dashboard, name='dashboard'),
]
