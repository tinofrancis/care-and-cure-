from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

class Doctor(User):
    class Meta:
        proxy = True
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(default=0, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    allergies = models.TextField(blank=True)
    medical_details = models.TextField(blank=True)
    lab_reports = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    
    # Advanced Clinical Metrics
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    blood_sugar = models.IntegerField(null=True, blank=True)  # mg/dL
    heart_rate = models.IntegerField(null=True, blank=True)   # bpm
    cholesterol = models.IntegerField(null=True, blank=True)  # LPT
    bilirubin = models.FloatField(null=True, blank=True)      # LFT
    alt = models.IntegerField(null=True, blank=True)           # LFT
    ast = models.IntegerField(null=True, blank=True)           # LFT

    doctors = models.ManyToManyField(User, related_name='patients_list', blank=True, limit_choices_to={'is_doctor': True})

    def __str__(self):
        return f"Patient Profile for {self.user.username}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100, blank=True)
    specialist = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Doctor Profile for {self.user.username}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Appointment: {self.patient.user.username} with {self.doctor.user.username} ({self.status})"
