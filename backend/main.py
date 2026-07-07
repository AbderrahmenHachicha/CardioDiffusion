from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from database import (
    init_db, get_db,
    create_patient, get_patient, get_all_patients,
    save_prediction, get_patient_history,
    Patient, Prediction
)
from model import predict
from llm import explain_prediction

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


# ── Schemas ──────────────────────────────────────────────────────────────────

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

class PredictionOut(BaseModel):
    id: int
    patient_id: int
    predicted_class: str
    confidence: float
    probabilities: dict
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


# ── Patients ──────────────────────────────────────────────────────────────────

@app.post("/patients", response_model=PatientOut, status_code=201)
def create_patient_route(body: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, name=body.name, age=body.age, gender=body.gender)


@app.get("/patients", response_model=List[PatientOut])
def list_patients_route(db: Session = Depends(get_db)):
    return get_all_patients(db)


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient_route(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# ── Predictions ───────────────────────────────────────────────────────────────

@app.post("/patients/{patient_id}/predict", response_model=PredictionOut, status_code=201)
def predict_route(patient_id: int, body: PredictRequest, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

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
    )


@app.get("/patients/{patient_id}/history", response_model=List[PredictionOut])
def history_route(patient_id: int, db: Session = Depends(get_db)):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return get_patient_history(db, patient_id)
