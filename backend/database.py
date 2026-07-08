import os
from datetime import datetime
from typing import List, Dict, Optional, Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Integer, Float, DateTime, ForeignKey, JSON, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/cardiodiffusion")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Doctor(Base):
    __tablename__ = "doctors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    patients: Mapped[List["Patient"]] = relationship(
        "Patient", back_populates="doctor", cascade="all, delete-orphan"
    )


class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    doctor: Mapped[Optional["Doctor"]] = relationship("Doctor", back_populates="patients")
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="patient", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    raw_signal: Mapped[List[float]] = mapped_column(JSON, nullable=False)
    predicted_class: Mapped[str] = mapped_column(String(5), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    patient: Mapped["Patient"] = relationship("Patient", back_populates="predictions")


def init_db():
    from .auth import get_password_hash
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Verify columns (manual check for doctor_id in patients)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if "patients" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("patients")]
            if "doctor_id" not in columns:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE patients ADD COLUMN doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE"))
                    print("[INFO] Added doctor_id column to patients table via raw SQL alter.")
        
        # Seed default doctors if none exist
        db = SessionLocal()
        try:
            doctor_count = db.query(Doctor).count()
            if doctor_count == 0:
                print("[INFO] Seeding default doctor accounts...")
                doc1 = Doctor(
                    username="doctor1",
                    password_hash=get_password_hash("password123"),
                    name="Dr. Sarah Jenkins"
                )
                doc2 = Doctor(
                    username="doctor2",
                    password_hash=get_password_hash("password123"),
                    name="Dr. Robert Chen"
                )
                db.add_all([doc1, doc2])
                db.commit()
                print("[INFO] Default doctors seeded successfully.")
        finally:
            db.close()
            
    except Exception as e:
        print(f"[WARNING] Could not initialize database: {e}")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_doctor(db: Session, username: str, password_hash: str, name: str) -> Doctor:
    doctor = Doctor(username=username, password_hash=password_hash, name=name)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor_by_username(db: Session, username: str) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.username == username).first()


def create_patient(db: Session, doctor_id: int, name: Optional[str] = None, age: Optional[int] = None, gender: Optional[str] = None) -> Patient:
    patient = Patient(doctor_id=doctor_id, name=name, age=age, gender=gender)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int, doctor_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()


def get_patient_by_name_and_doctor(db: Session, name: str, doctor_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(
        Patient.name.ilike(name.strip()), 
        Patient.doctor_id == doctor_id
    ).first()


def get_all_patients(db: Session, doctor_id: int) -> List[Patient]:
    return db.query(Patient).filter(Patient.doctor_id == doctor_id).all()


def save_prediction(
    db: Session,
    patient_id: int,
    raw_signal: List[float],
    predicted_class: str,
    confidence: float,
    probabilities: Dict[str, float]
) -> Prediction:
    prediction = Prediction(
        patient_id=patient_id,
        raw_signal=raw_signal,
        predicted_class=predicted_class,
        confidence=confidence,
        probabilities=probabilities
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_patient_history(db: Session, patient_id: int) -> List[Prediction]:
    return db.query(Prediction).filter(Prediction.patient_id == patient_id).order_by(Prediction.created_at.desc()).all()


def delete_patient(db: Session, patient_id: int, doctor_id: int) -> bool:
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.doctor_id == doctor_id).first()
    if not patient:
        return False
    db.delete(patient)
    db.commit()
    return True
