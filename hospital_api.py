from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

# -------------------------------
# Initialize FastAPI
# -------------------------------
app = FastAPI(title="Hospital Appointment System")

# -------------------------------
# Allowed Data Sets
# -------------------------------
ALLOWED_PATIENTS = {"P001", "P002", "P003", "P004"}
ALLOWED_DOCTORS = {
    "D101": {"name": "Dr. Alice", "specialty": "Cardiologist"},
    "D102": {"name": "Dr. Bob", "specialty": "Dermatologist"},
    "D103": {"name": "Dr. Clara", "specialty": "Neurologist"},
    "D104": {"name": "Dr. David", "specialty": "Orthopedic"},
}

# Mock storage for appointments
APPOINTMENTS = {}

# -------------------------------
# Pydantic Models
# -------------------------------
class Patient(BaseModel):
    patient_id: str

class DoctorSpecialty(BaseModel):
    specialty: str

class AppointmentBooking(BaseModel):
    patient_id: str
    doctor_id: str
    date: str  # format: YYYY-MM-DD

class RescheduleAppointment(BaseModel):
    appointment_id: str
    new_date: str  # format: YYYY-MM-DD

class Payment(BaseModel):
    patient_id: str
    amount: float

# -------------------------------
# Patient ID Validation
# -------------------------------
@app.post("/validate-patient/")
def validate_patient(patient: Patient):
    if patient.patient_id in ALLOWED_PATIENTS:
        return {"message": "Patient ID is valid!", "patient_id": patient.patient_id}
    else:
        return {"message": "Patient ID is invalid!"}

# -------------------------------
# RE-Validate Patient ID
# -------------------------------
@app.post("/re-validate-patient/")
def re_validate_patient(patient: Patient):
    if patient.patient_id in ALLOWED_PATIENTS:
        return {"message": "Re-entered Patient ID is valid!", "patient_id": patient.patient_id}
    else:
        return {"message": "Re-entered Patient ID is invalid!"}

# -------------------------------
# View Available Doctors by Specialty
# -------------------------------
@app.post("/view-doctors/")
def view_doctors(specialty: DoctorSpecialty):
    doctors = [
        {"doctor_id": doc_id, "name": details["name"], "specialty": details["specialty"]}
        for doc_id, details in ALLOWED_DOCTORS.items()
        if details["specialty"].lower() == specialty.specialty.lower()
    ]
    if not doctors:
        return {"message": f"No doctors available for specialty: {specialty.specialty}"}
    return {"available_doctors": doctors}

# -------------------------------
# Re-verify Doctor ID
# -------------------------------
@app.post("/re-verify-doctor/")
def re_verify_doctor(doctor_id: str):
    if doctor_id in ALLOWED_DOCTORS:
        return {"message": "Re-entered Doctor ID is valid!", "doctor_id": doctor_id}
    else:
        return {"message": "Re-entered Doctor ID is invalid!"}

# -------------------------------
# Book Appointment
# -------------------------------
@app.post("/book-appointment/")
def book_appointment(booking: AppointmentBooking):
    if booking.patient_id not in ALLOWED_PATIENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient ID not found.")
    if booking.doctor_id not in ALLOWED_DOCTORS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor ID not found.")

    appointment_id = f"A{random.randint(1000,9999)}"
    slot = random.choice(["10:00 AM", "11:30 AM", "2:00 PM", "4:00 PM"])
    appointment_date = booking.date

    APPOINTMENTS[appointment_id] = {
        "patient_id": booking.patient_id,
        "doctor_id": booking.doctor_id,
        "date": appointment_date,
        "slot": slot
    }

    return {
        "message": "Appointment booked successfully!",
        "appointment_id": appointment_id,
        "patient_id": booking.patient_id,
        "doctor_id": booking.doctor_id,
        "date": appointment_date,
        "slot": slot
    }

# -------------------------------
# Reschedule Appointment
# -------------------------------
@app.post("/reschedule-appointment/")
def reschedule_appointment(reschedule: RescheduleAppointment):
    if reschedule.appointment_id not in APPOINTMENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    new_slot = random.choice(["9:30 AM", "12:00 PM", "3:00 PM", "5:30 PM"])
    APPOINTMENTS[reschedule.appointment_id]["date"] = reschedule.new_date
    APPOINTMENTS[reschedule.appointment_id]["slot"] = new_slot

    return {
        "message": "Appointment rescheduled successfully!",
        "appointment_id": reschedule.appointment_id,
        "new_date": reschedule.new_date,
        "new_slot": new_slot
    }

# -------------------------------
# Payment for Consultation
# -------------------------------
@app.post("/pay-consultation/")
def pay_consultation(payment: Payment):
    if payment.patient_id not in ALLOWED_PATIENTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient ID not found.")
    if payment.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment amount must be greater than zero.")

    transaction_id = f"T{random.randint(100000,999999)}"
    return {
        "message": "Payment successful!",
        "patient_id": payment.patient_id,
        "amount_paid": payment.amount,
        "transaction_id": transaction_id
    }
