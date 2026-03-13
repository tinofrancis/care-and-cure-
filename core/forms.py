from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PatientProfile, DoctorProfile, Appointment

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField(required=False, min_value=0, max_value=120)
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, required=False)
    allergies = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Type to search allergies...', 'list': 'allergy-list'}), required=False)
    medical_details = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                age=self.cleaned_data.get('age', 0),
                gender=self.cleaned_data.get('gender', ''),
                allergies=self.cleaned_data.get('allergies', ''),
                medical_details=self.cleaned_data.get('medical_details', '')
            )
        return user

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['age', 'gender', 'allergies', 'medical_details', 'lab_reports']
        widgets = {
            'allergies': forms.TextInput(attrs={'placeholder': 'Type to search allergies...', 'list': 'allergy-list'}),
            'medical_details': forms.Textarea(attrs={'rows': 5}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['degree', 'specialist']

class ClinicalMetricsForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic', 
            'blood_sugar', 'heart_rate', 'cholesterol', 
            'bilirubin', 'alt', 'ast'
        ]
        widgets = {
            'blood_pressure_systolic': forms.NumberInput(attrs={'placeholder': 'Systolic'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'placeholder': 'Diastolic'}),
        }

class PrescriptionForm(forms.Form):
    prescription_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Enter prescription text (simulated handwriting)", required=False)
    prescription_image = forms.ImageField(label="Scan Prescription Image", required=False)

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Explain your issue (e.g. "I think I have a bone fracture in my leg" or "Severe toothache")'
            }),
        }
