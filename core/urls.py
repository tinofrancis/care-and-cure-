from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    dashboard, register, login_view, patient_profile,
    upload_prescription, analyze, doctor_patient_detail, assign_doctor,
    request_appointment, handle_appointment, chat_api
)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', patient_profile, name='patient_profile'),
    path('upload-prescription/', upload_prescription, name='upload_prescription'),
    path('analyze/', analyze, name='analyze'),
    path('patient/<int:pk>/', doctor_patient_detail, name='doctor_patient_detail'),
    path('assign-doctor/<int:patient_id>/', assign_doctor, name='assign_doctor'),
    path('appointment/request/', request_appointment, name='request_appointment'),
    path('appointment/<int:pk>/<str:action>/', handle_appointment, name='handle_appointment'),
    path('api/chat/', chat_api, name='chat_api'),
]
