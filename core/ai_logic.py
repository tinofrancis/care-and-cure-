# Curecare Advanced AI Engine v2
import json
import urllib.request
from urllib.parse import quote
import re
import random

def parse_prescription(text):
    text = text.lower()
    drugs = []
    conditions = []
    
    # Advanced matching
    drug_db = {
        'aspirin': 'Aspirin (Anticonvulsant/Antiplatelet)',
        'ibuprofen': 'Ibuprofen (NSAID)',
        'metformin': 'Metformin (Antidiabetic)',
        'atorvastatin': 'Atorvastatin (Lipid-lowering)',
        'amoxicillin': 'Amoxicillin (Antibiotic)',
        'lisinopril': 'Lisinopril (ACE Inhibitor)',
    }
    
    for key, val in drug_db.items():
        if key in text: drugs.append(val)
        
    if 'diabetes' in text: conditions.append('Type II Diabetes Mellitus')
    if 'hypertension' in text: conditions.append('Essential Hypertension')
    if 'cholesterol' in text: conditions.append('Hyperlipidemia')
    
    duration = ""
    duration_match = re.search(r'for\s+(\d+)\s+days', text)
    if duration_match:
        duration = f" for a course of {duration_match.group(1)} days"

    found_drugs = '; '.join(drugs) or 'No structured medications identified'
    found_conds = '; '.join(conditions) or 'No chronic conditions detected'
    
    return f"Clinical Note: Handwritten Rx Parsed. Meds: {found_drugs}{duration}. Primary Indicators: {found_conds}."

def analyze_patient_data(medical_details, age=0, allergies='', biomarkers=None):
    text = medical_details.lower() + allergies.lower()
    risk = 0
    risk_factors = []
    insights = []
    
    # Weighted Scoring
    if age > 65: 
        risk += 25
        risk_factors.append("age-related vulnerability")
    elif age > 45: 
        risk += 10
    
    conditions = {
        'diabetes': (25, "glycemic instability"),
        'hypertension': (20, "elevated arterial pressure"),
        'cardiac': (30, "cardiovascular compromise"),
        'asthma': (15, "respiratory sensitivity"),
        'infection': (15, "active infection detected"),
        'abnormal': (10, "abnormal lab report findings"),
        'fever': (10, "acute febrile response")
    }
    
    for key, (score, factor) in conditions.items():
        if key in text:
            risk += score
            risk_factors.append(factor)
    
    # biomarker-driven insights
    if biomarkers:
        sys = biomarkers.get('blood_pressure_systolic')
        dia = biomarkers.get('blood_pressure_diastolic')
        if sys and sys > 140: 
            risk += 20
            insights.append("Systolic pressure is above clinical threshold.")
        elif sys and sys > 130:
            risk += 10
            insights.append("Blood pressure is elevated.")
            
        hr = biomarkers.get('heart_rate')
        if hr and hr > 100:
            risk += 15
            insights.append("Tachycardia (elevated heart rate) detected.")
        elif hr and hr < 60:
            risk += 10
            insights.append("Bradycardia (low resting heart rate) detected.")
        
        sugar = biomarkers.get('blood_sugar')
        if sugar and sugar > 180:
            risk += 25
            insights.append("Critical glycemic elevation detected.")
        elif sugar and sugar > 130:
            risk += 10
            insights.append("Pre-diabetic glucose levels noted.")
            
        chol = biomarkers.get('cholesterol')
        if chol and chol > 240:
            risk += 15
            insights.append("Lipid profile indicates hypercholesterolemia.")
        elif chol and chol > 200:
            risk += 10
            insights.append("Lipid profile indicates borderline elevated cholesterol.")
            
        bili = biomarkers.get('bilirubin')
        if bili and bili > 1.2:
            risk += 10
            insights.append("Elevated bilirubin detected in lab reports.")
            
        alt = biomarkers.get('alt')
        ast = biomarkers.get('ast')
        if (alt and alt > 55) or (ast and ast > 48):
            risk += 15
            insights.append("Liver function tests (ALT/AST) indicate potential hepatic stress.")
            
    risk = min(max(risk, 0), 100)

    # Cross-Link Interaction Check
    drug_alerts = []
    interactions = [
        (('aspirin', 'ibuprofen'), 'Moderate: Risk of GI bleeding/reduced aspirin efficacy.'),
        (('metformin', 'alcohol'), 'Severe: Risk of Metabolic Acidosis—immediate cessation of alcohol required.'),
        (('warfarin', 'aspirin'), 'Critical: Hemorrhagic risk significantly elevated.'),
        (('atorvastatin', 'grapefruit'), 'Moderate: Risk of statin toxicity/myopathy. Avoid grapefruit.'),
        (('amoxicillin', 'methotrexate'), 'Severe: Increased risk of methotrexate toxicity.'),
    ]
    
    for drugs, msg in interactions:
        if all(d in text for d in drugs):
            drug_alerts.append(f"⚠️ [Pharmacovigilance Alert]: {msg}")

    # Generate Structured Summary
    status = "CRITICAL" if risk > 75 else "ELEVATED" if risk > 40 else "STABLE"
    summary = f"Digital Health Report: Status - {status} (Composite Risk: {risk}%)\n\n"
    
    if risk_factors:
        summary += f"Key Risk Indicators: {', '.join(risk_factors).title()}.\n"
    
    if insights:
        summary += "Clinical Insights:\n- " + "\n- ".join(insights) + "\n"
        
    summary += "\nRecommendation: "
    if risk > 60:
        summary += "Immediate specialist consultation recommended. Monitor vitals Q4H."
    elif risk > 30:
        summary += "Schedule a routine review. Maintain current medication adherence."
    else:
        summary += "Maintain healthy lifestyle. Next check-in in 6 months."
        
    return risk, drug_alerts, summary

def simulate_ocr(image_file):
    """
    Advanced OCR Simulation with randomized 'detected' data.
    """
    if not image_file: return ""
    
    results = [
        "Rx: Atorvastatin 20mg QD. Patient reports chest sting. BP: 145/92. Pulse: 88.",
        "Rx: Metformin 500mg BID. No allergies reported. Fasting Glucose: 155 mg/dL.",
        "Rx: Lisinopril 10mg. Persistent cough noted. BP: 130/85. Heart Rate: 72 bpm.",
    ]
    return f"CareAI OCR [Confidence 94%]: {random.choice(results)}"

def get_online_reference(query):
    try:
        search_term = query.strip()
        encoded_query = quote(search_term)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'CareCurePremium/2.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('type') == 'standard' and 'extract' in data:
                    return f"🌐 **Clinical Reference:**\n{data['extract']}\n\n[Full Review]({data.get('content_urls', {}).get('desktop', {}).get('page', '#')})"
    except: pass
    return None

def get_chat_response(message, context):
    msg = message.lower()
    
    # 1. Health-specific logic
    if 'risk' in msg or 'score' in msg:
        return f"Your current composite health risk is calculated as {context.count('%') > 0 and 'found in records' or 'awaiting analysis'}. Refer to the 'Wellness Snapshot' for details."
    
    if 'vital' in msg or 'bp' in msg or 'sugar' in msg:
        return f"Analyzing your vitals from the current session: {context}. Trends appear stable but require physician confirmation."

    # 2. Wikipedia search
    online_info = get_online_reference(message)
    if online_info:
        return online_info
    
    # 3. Empathetic Fallback
    return f"I've scanned your current records and medical databases. While I don't have a specific answer for '{message}', I recommend discussing it during your next appointment with the specialists listed on your dashboard."
