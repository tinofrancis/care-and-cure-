
import os
import sys
import django
import random
from datetime import timedelta

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carecure.settings")
django.setup()

from django.utils import timezone
from core.models import User, DoctorProfile, PatientProfile, Appointment

def create_users():
    """Creates and saves doctor and patient users."""
    doctors_data = [
        {"username": "DrAlice", "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "degree": "MD", "specialist": "Cardiologist"},
        {"username": "DrBob", "first_name": "Bob", "last_name": "Johnson", "email": "bob@example.com", "degree": "DO", "specialist": "Neurologist"},
        {"username": "DrCarol", "first_name": "Carol", "last_name": "Williams", "email": "carol@example.com", "degree": "MD", "specialist": "Dermatologist"},
        {"username": "DrDavid", "first_name": "David", "last_name": "Jones", "email": "david@example.com", "degree": "MD", "specialist": "Pediatrician"},
        {"username": "DrEmily", "first_name": "Emily", "last_name": "Brown", "email": "emily@example.com", "degree": "DO", "specialist": "Oncologist"},
    ]
    patients_data = [
        {"username": "Charlie", "first_name": "Charlie", "last_name": "Brown", "email": "charlie@example.com", "age": 34, "gender": "M", "allergies": "Peanuts", "medical_details": "History of asthma.", "blood_pressure_systolic": 120, "blood_pressure_diastolic": 80, "blood_sugar": 90, "heart_rate": 70, "cholesterol": 180, "bilirubin": 0.8, "alt": 25, "ast": 30},
        {"username": "Diana", "first_name": "Diana", "last_name": "Miller", "email": "diana@example.com", "age": 45, "gender": "F", "allergies": "None", "medical_details": "Generally healthy.", "blood_pressure_systolic": 130, "blood_pressure_diastolic": 85, "blood_sugar": 100, "heart_rate": 75, "cholesterol": 200, "bilirubin": 0.6, "alt": 20, "ast": 25},
        {"username": "Eve", "first_name": "Eve", "last_name": "Davis", "email": "eve@example.com", "age": 28, "gender": "F", "allergies": "Pollen", "medical_details": "Seasonal allergies.", "blood_pressure_systolic": 110, "blood_pressure_diastolic": 70, "blood_sugar": 85, "heart_rate": 65, "cholesterol": 160, "bilirubin": 0.7, "alt": 15, "ast": 20},
        {"username": "Frank", "first_name": "Frank", "last_name": "Garcia", "email": "frank@example.com", "age": 56, "gender": "M", "allergies": "None", "medical_details": "High blood pressure.", "blood_pressure_systolic": 140, "blood_pressure_diastolic": 90, "blood_sugar": 110, "heart_rate": 80, "cholesterol": 220, "bilirubin": 0.9, "alt": 30, "ast": 35},
        {"username": "Grace", "first_name": "Grace", "last_name": "Rodriguez", "email": "grace@example.com", "age": 67, "gender": "F", "allergies": "Penicillin", "medical_details": "Osteoarthritis.", "blood_pressure_systolic": 135, "blood_pressure_diastolic": 88, "blood_sugar": 105, "heart_rate": 78, "cholesterol": 210, "bilirubin": 0.5, "alt": 18, "ast": 22},
        {"username": "Heidi", "first_name": "Heidi", "last_name": "Wilson", "email": "heidi@example.com", "age": 19, "gender": "F", "allergies": "None", "medical_details": "Acne.", "blood_pressure_systolic": 115, "blood_pressure_diastolic": 75, "blood_sugar": 95, "heart_rate": 72, "cholesterol": 170, "bilirubin": 0.6, "alt": 22, "ast": 28},
        {"username": "Ivan", "first_name": "Ivan", "last_name": "Martinez", "email": "ivan@example.com", "age": 42, "gender": "M", "allergies": "Shellfish", "medical_details": "None.", "blood_pressure_systolic": 125, "blood_pressure_diastolic": 82, "blood_sugar": 98, "heart_rate": 74, "cholesterol": 190, "bilirubin": 0.7, "alt": 28, "ast": 32},
        {"username": "Judy", "first_name": "Judy", "last_name": "Anderson", "email": "judy@example.com", "age": 31, "gender": "F", "allergies": "Dust mites", "medical_details": "Eczema.", "blood_pressure_systolic": 118, "blood_pressure_diastolic": 78, "blood_sugar": 92, "heart_rate": 68, "cholesterol": 175, "bilirubin": 0.9, "alt": 26, "ast": 31},
    ]

    for data in doctors_data:
        user, created = User.objects.get_or_create(username=data["username"], defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "is_doctor": True,
        })
        if created:
            user.set_password("password")
            user.save()
            DoctorProfile.objects.create(user=user, degree=data["degree"], specialist=data["specialist"])

    for data in patients_data:
        user, created = User.objects.get_or_create(username=data["username"], defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "is_patient": True,
        })
        if created:
            user.set_password("password")
            user.save()
            PatientProfile.objects.create(
                user=user, 
                age=data["age"], 
                gender=data["gender"],
                allergies=data["allergies"],
                medical_details=data["medical_details"],
                blood_pressure_systolic=data["blood_pressure_systolic"],
                blood_pressure_diastolic=data["blood_pressure_diastolic"],
                blood_sugar=data["blood_sugar"],
                heart_rate=data["heart_rate"],
                cholesterol=data["cholesterol"],
                bilirubin=data["bilirubin"],
                alt=data["alt"],
                ast=data["ast"]
            )

def populate_database():
    """Populates the database with sample data."""
    print("Deleting existing data...")
    Appointment.objects.all().delete()
    PatientProfile.objects.all().delete()
    DoctorProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    print("Creating users...")
    create_users()

    print("Linking doctors and patients...")
    doctors = DoctorProfile.objects.all()
    patients = PatientProfile.objects.all()

    for patient_profile in patients:
        # Assign 1 to 2 random doctors to each patient
        num_doctors = random.randint(1, len(doctors))
        assigned_doctors = random.sample(list(doctors), num_doctors)
        for doctor_profile in assigned_doctors:
            patient_profile.doctors.add(doctor_profile.user)
    
    print("Creating appointments...")
    for patient_profile in patients:
        # Create 1 to 3 appointments for each patient
        for _ in range(random.randint(1, 3)):
            doctor_profile = random.choice(patient_profile.doctors.all())
            doctor_profile = DoctorProfile.objects.get(user=doctor_profile)
            Appointment.objects.create(
                patient=patient_profile,
                doctor=doctor_profile,
                reason=random.choice(["Routine Checkup", "Follow-up", "New Issue"]),
                status=random.choice(['PENDING', 'CONFIRMED', 'CANCELLED']),
                appointment_date=timezone.now() + timedelta(days=random.randint(1, 30))
            )

    print("Database populated successfully!")

if __name__ == "__main__":
    populate_database()
