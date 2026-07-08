from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .database import (
    init_db, get_db,
    create_patient, get_patient, get_all_patients, get_patient_by_name_and_doctor,
    save_prediction, get_patient_history, delete_patient, create_doctor,
    Patient, Prediction, Doctor
)
from .model import predict
from .llm import explain_prediction
from .auth import verify_password, create_access_token, decode_access_token, get_password_hash

app = FastAPI(title="CardioDiffusion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# Security / Authentication Dependecy
security = HTTPBearer()

def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Doctor:
    token = credentials.credentials
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
    doctor = get_doctor_by_username_helper(db, username)
    if not doctor:
        raise HTTPException(status_code=401, detail="Doctor not found")
    return doctor

def get_doctor_by_username_helper(db: Session, username: str) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.username == username).first()


# Schemas 

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    name: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    doctor_name: str

class DoctorOut(BaseModel):
    id: int
    username: str
    name: str

    class Config:
        from_attributes = True

class PatientCreate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class PatientOut(BaseModel):
    id: int
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]

    class Config:
        from_attributes = True

class PredictRequest(BaseModel):
    signal: List[float]  # raw ECG signal, 187 floats expected

class PredictByNameRequest(BaseModel):
    patient_name: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    signal: List[float]

class PredictionOut(BaseModel):
    id: int
    patient_id: int
    predicted_class: str
    confidence: float
    probabilities: dict
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Endpoints

@app.post("/signup", response_model=LoginResponse, status_code=201)
def signup_route(body: SignupRequest, db: Session = Depends(get_db)):
    # Clean username
    username_cleaned = body.username.strip().lower()
    if not username_cleaned:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Full name cannot be empty")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
    existing_doctor = get_doctor_by_username_helper(db, username_cleaned)
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Username is already registered")
        
    # Format doctor name with Dr. prefix and Title Case
    raw_name = body.name.strip()
    name_lower = raw_name.lower()
    if not (name_lower.startswith("dr.") or name_lower.startswith("dr ")):
        formatted_name = f"Dr. {raw_name.title()}"
    else:
        if name_lower.startswith("dr."):
            rest = raw_name[3:].strip().title()
            formatted_name = f"Dr. {rest}"
        else:
            rest = raw_name[2:].strip().title()
            formatted_name = f"Dr. {rest}"

    hashed_pwd = get_password_hash(body.password)
    doctor = create_doctor(db, username=username_cleaned, password_hash=hashed_pwd, name=formatted_name)
    
    token = create_access_token(subject=doctor.username)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        doctor_name=doctor.name
    )

@app.post("/login", response_model=LoginResponse)
def login_route(body: LoginRequest, db: Session = Depends(get_db)):
    doctor = get_doctor_by_username_helper(db, body.username.strip().lower())
    if not doctor or not verify_password(body.password, doctor.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = create_access_token(subject=doctor.username)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        doctor_name=doctor.name
    )

@app.get("/me", response_model=DoctorOut)
def get_me_route(current_doctor: Doctor = Depends(get_current_doctor)):
    return current_doctor


# Patients

@app.post("/patients", response_model=PatientOut, status_code=201)
def create_patient_route(
    body: PatientCreate, 
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    return create_patient(db, doctor_id=current_doctor.id, name=body.name, age=body.age, gender=body.gender)


@app.get("/patients", response_model=List[PatientOut])
def list_patients_route(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    return get_all_patients(db, doctor_id=current_doctor.id)


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient_route(
    patient_id: int, 
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    patient = get_patient(db, patient_id, current_doctor.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")
    return patient


@app.delete("/patients/{patient_id}", status_code=204)
def delete_patient_route(
    patient_id: int,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    deleted = delete_patient(db, patient_id, current_doctor.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")
    return None


# Predictions

@app.post("/predict", response_model=PredictionOut, status_code=201)
def predict_by_name_route(
    body: PredictByNameRequest,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    if not body.patient_name or not body.patient_name.strip():
        raise HTTPException(status_code=400, detail="Patient name is required")
        
    # Find existing patient or create new one
    patient = get_patient_by_name_and_doctor(db, body.patient_name, current_doctor.id)
    if not patient:
        patient = create_patient(
            db, 
            doctor_id=current_doctor.id, 
            name=body.patient_name.strip(), 
            age=body.patient_age, 
            gender=body.patient_gender
        )
    else:
        # Optionally update age/gender if provided and missing
        updated = False
        if body.patient_age is not None and patient.age is None:
            patient.age = body.patient_age
            updated = True
        if body.patient_gender is not None and patient.gender is None:
            patient.gender = body.patient_gender
            updated = True
        if updated:
            db.commit()
            db.refresh(patient)
            
    # Run prediction
    result = predict(body.signal)
    explanation = explain_prediction(result)
    
    # Save prediction
    record = save_prediction(
        db,
        patient_id=patient.id,
        raw_signal=body.signal,
        predicted_class=result["class"],
        confidence=result["confidence"],
        probabilities=result["probabilities"]
    )
    
    return PredictionOut(
        id=record.id,
        patient_id=record.patient_id,
        predicted_class=record.predicted_class,
        confidence=record.confidence,
        probabilities=record.probabilities,
        explanation=explanation,
        created_at=record.created_at
    )


@app.post("/patients/{patient_id}/predict", response_model=PredictionOut, status_code=201)
def predict_route(
    patient_id: int, 
    body: PredictRequest, 
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    patient = get_patient(db, patient_id, current_doctor.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")

    result = predict(body.signal)
    explanation = explain_prediction(result)

    record = save_prediction(
        db,
        patient_id=patient_id,
        raw_signal=body.signal,
        predicted_class=result["class"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
    )

    return PredictionOut(
        id=record.id,
        patient_id=record.patient_id,
        predicted_class=record.predicted_class,
        confidence=record.confidence,
        probabilities=record.probabilities,
        explanation=explanation,
        created_at=record.created_at
    )


@app.get("/patients/{patient_id}/history", response_model=List[PredictionOut])
def history_route(
    patient_id: int, 
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    patient = get_patient(db, patient_id, current_doctor.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or unauthorized")
    return get_patient_history(db, patient_id)
