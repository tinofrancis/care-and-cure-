from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import PatientRegistrationForm, PatientProfileForm, PrescriptionForm, DoctorProfileForm, ClinicalMetricsForm, AppointmentRequestForm
from .models import PatientProfile, User, DoctorProfile, Appointment
from .ai_logic import analyze_patient_data, parse_prescription, simulate_ocr, get_chat_response
import json
import re

# ... (rest of previous imports)

@login_required
def request_appointment(request):
    if not request.user.is_patient:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patientprofile
            reason = appointment.reason.lower()
            
            # Robust Smart Routing Logic
            specialty_map = {
                'ortho': ['bone', 'fracture', 'joint', 'spine', 'muscle', 'leg', 'arm', 'injury', 'back pain', 'knee', 'shoulder', 'sprain'],
                'cardio': ['heart', 'chest', 'palpitation', 'breath', 'blood pressure', 'hypertension', 'vessels', 'pulse', 'cholesterol'],
                'derm': ['skin', 'rash', 'itch', 'acne', 'mole', 'burn', 'dermatology', 'eczema', 'psoriasis'],
                'dental': ['tooth', 'gum', 'mouth', 'dentist', 'cavity', 'filling', 'crown', 'braces'],
                'internal': ['fever', 'cold', 'flu', 'stomach', 'digestion', 'headache', 'weakness', 'fatigue', 'diabetes', 'thyroid'],
                'neuro': ['brain', 'nerve', 'seizure', 'dizziness', 'numbness', 'tremor', 'migraine', 'balance'],
                'ent': ['ear', 'nose', 'throat', 'hearing', 'sinus', 'tonsil', 'voice']
            }
            
            target_specialty = None
            for specialty, keywords in specialty_map.items():
                if any(k in reason for k in keywords):
                    target_specialty = specialty
                    break
            
            matched_doctor = None
            doctors = DoctorProfile.objects.all()
            
            if target_specialty:
                # Priority 1: Match exactly by specialty keyword
                matched_doctor = doctors.filter(specialist__icontains=target_specialty).first()
            
            # Priority 2: Fallback to the doctor with the most relevant bio/description
            if not matched_doctor:
                # Try partial match on the reason text against doctor specialist field
                for doc in doctors:
                    if doc.specialist.lower() in reason:
                        matched_doctor = doc
                        break
            
            # Priority 3: Fallback to general/internal medicine
            if not matched_doctor:
                matched_doctor = doctors.filter(specialist__icontains='internal').first() or doctors.first()
            
            if matched_doctor:
                appointment.doctor = matched_doctor
                appointment.save()
                return redirect('dashboard')
            else:
                form.add_error(None, "Our AI couldn't route your request to a specialist. Please try again with more details or contact support.")
    else:
        form = AppointmentRequestForm()
    
    return render(request, 'core/request_appointment.html', {'form': form})

@login_required
def handle_appointment(request, pk, action):
    if not request.user.is_doctor:
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctorprofile)
    if action == 'confirm':
        appointment.status = 'CONFIRMED'
    elif action == 'cancel':
        appointment.status = 'CANCELLED'
    
    appointment.save()
    return redirect('dashboard')

def register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_patient:
        profile, created = PatientProfile.objects.get_or_create(user=request.user)
        doctors_info = []
        for doctor in profile.doctors.all():
            doc_profile = getattr(doctor, 'doctorprofile', None)
            doctors_info.append({
                'name': doctor.get_full_name() or doctor.username,
                'degree': doc_profile.degree if doc_profile else 'N/A',
                'specialist': doc_profile.specialist if doc_profile else 'N/A'
            })
        appointments = Appointment.objects.filter(patient=profile).order_by('-created_at')
        return render(request, 'core/dashboard.html', {
            'profile': profile, 
            'doctors_info': doctors_info,
            'appointments': appointments
        })
    elif request.user.is_doctor:
        patients = request.user.patients_list.all()
        doc_profile = getattr(request.user, 'doctorprofile', None)
        appointments = Appointment.objects.filter(doctor=doc_profile, status='PENDING').order_by('-created_at')
        doctor_info = {
            'name': request.user.get_full_name() or request.user.username,
            'degree': doc_profile.degree if doc_profile else 'N/A',
            'specialist': doc_profile.specialist if doc_profile else 'N/A'
        }
        return render(request, 'core/dashboard.html', {
            'patients': patients, 
            'doctor_info': doctor_info,
            'pending_appointments': appointments
        })
    return redirect('login')

@login_required
def patient_profile(request):
    if not request.user.is_patient:
        return redirect('dashboard')
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PatientProfileForm(instance=profile)
    return render(request, 'core/patient_profile.html', {'form': form, 'profile': profile})

@login_required
def upload_prescription(request):
    if not request.user.is_patient:
        return redirect('dashboard')
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data.get('prescription_text', '')
            image = form.cleaned_data.get('prescription_image')
            
            if image:
                # OCR Simulation with better parsing logic
                ocr_text = simulate_ocr(image)
                text = f"{text}\n{ocr_text}".strip()
                
                profile = request.user.patientprofile
                
                # Refined extraction regex
                extractors = [
                    (r'BP.*?(\d{2,3})/(\d{2,3})', ['blood_pressure_systolic', 'blood_pressure_diastolic']),
                    (r'Sugar.*?(\d{2,3})', ['blood_sugar']),
                    (r'Heart Rate.*?(\d{2,3})', ['heart_rate']),
                    (r'Pulse.*?(\d{2,3})', ['heart_rate']),
                    (r'Cholesterol.*?(\d{2,3})', ['cholesterol']),
                ]
                
                for pattern, fields in extractors:
                    match = re.search(pattern, ocr_text, re.IGNORECASE)
                    if match:
                        for i, field in enumerate(fields):
                            setattr(profile, field, int(match.group(i+1)))
                
                profile.save()
            
            parsed = parse_prescription(text)
            profile = request.user.patientprofile
            profile.medical_details += f"\n\n[Prescription Analysis {request.user.username}]\nOriginal: {text}\nFindings: {parsed}\n---"
            profile.save()
            return redirect('analyze')
    else:
        form = PrescriptionForm()
    return render(request, 'core/upload_prescription.html', {'form': form})

@login_required
def analyze(request):
    if not request.user.is_patient:
        return redirect('dashboard')
    profile = request.user.patientprofile
    biomarkers = profile.__dict__ # Passing full dict for more data points
    
    risk_score, drug_alerts, summary = analyze_patient_data(
        profile.medical_details, profile.age, profile.allergies, biomarkers=biomarkers
    )
    return render(request, 'core/analysis_result.html', {
        'risk_score': risk_score,
        'drug_alerts': drug_alerts,
        'summary': summary,
    })

@login_required
def doctor_patient_detail(request, pk):
    if not request.user.is_doctor:
        return redirect('dashboard')
    patient = get_object_or_404(PatientProfile, pk=pk)
    if patient not in request.user.patients_list.all():
        return redirect('dashboard')
    
    risk_score, drug_alerts, summary = analyze_patient_data(
        patient.medical_details, patient.age, patient.allergies, biomarkers=patient.__dict__
    )
    
    form = ClinicalMetricsForm(instance=patient)
    if request.method == 'POST':
        form = ClinicalMetricsForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('doctor_patient_detail', pk=pk)

    return render(request, 'core/doctor_patient_detail.html', {
        'patient': patient,
        'risk_score': risk_score,
        'drug_alerts': drug_alerts,
        'summary': summary,
        'form': form
    })

@login_required
def assign_doctor(request, patient_id):
    if not request.user.is_doctor:
        return redirect('dashboard')
    patient = get_object_or_404(PatientProfile, id=patient_id)
    patient.doctors.add(request.user)
    return redirect('dashboard')

def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        message = data.get('message', '')
        url = data.get('url', '')
        
        context_parts = []
        
        if request.user.is_authenticated:
            if request.user.is_doctor:
                context_parts.append(f"User is Doctor {request.user.get_full_name()}.")
                match = re.search(r'/patient/(\d+)', url)
                if match:
                    try:
                        p = PatientProfile.objects.get(pk=match.group(1))
                        context_parts.append(f"Current Subject: Patient {p.user.get_full_name()}. Age: {p.age}. Vitals: {p.blood_pressure_systolic}/{p.blood_pressure_diastolic}. Medical History: {p.medical_details[:500]}...")
                    except: pass
            elif request.user.is_patient:
                context_parts.append(f"User is Patient {request.user.get_full_name()}.")
                try:
                    p = request.user.patientprofile
                    context_parts.append(f"Patient Health Background: Age {p.age}, Allergies: {p.allergies}. History: {p.medical_details[:300]}...")
                except: pass
        else:
            context_parts.append("User is a Guest explorer.")

        context = " ".join(context_parts)
        response_text = get_chat_response(message, context)
        return JsonResponse({'reply': response_text})
    return JsonResponse({'error': 'Invalid request'}, status=400)
