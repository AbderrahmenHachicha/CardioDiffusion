import os
from datetime import datetime
from typing import List, Dict, Optional, Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

# Load environment variables from .env file
load_dotenv()

# Fallback default connection details for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cardiodiffusion")

# Create engine and session maker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy model declarations."""
    pass

class Patient(Base):
    """
    Patient table schema storing demographics and identifying info.
    """
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # One-to-many relationship with predictions
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction", back_populates="patient", cascade="all, delete-orphan"
    )

class Prediction(Base):
    """
    Predictions table storing incoming raw ECG signals and classification results.
    """
    __tablename__ = "predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    raw_signal: Mapped[List[float]] = mapped_column(JSON, nullable=False)  # 187 floats
    predicted_class: Mapped[str] = mapped_column(String(5), nullable=False)  # N, A, V, L, R
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Back relation to Patient
    patient: Mapped["Patient"] = relationship("Patient", back_populates="predictions")


def init_db():
    """Initializes the database by creating all declared tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a thread-safe database session
    and automatically handles closing it when finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# CRUD & Database Helper Functions
# ==========================================

def create_patient(db: Session, name: Optional[str] = None, age: Optional[int] = None, gender: Optional[str] = None) -> Patient:
    """Creates a new patient profile in the database."""
    patient = Patient(name=name, age=age, gender=gender)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    """Retrieves a single patient profile by ID."""
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_all_patients(db: Session) -> List[Patient]:
    """Retrieves all registered patient profiles."""
    return db.query(Patient).all()

def save_prediction(
    db: Session,
    patient_id: int,
    raw_signal: List[float],
    predicted_class: str,
    confidence: float,
    probabilities: Dict[str, float]
) -> Prediction:
    """Saves an ECG prediction result associated with a patient."""
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
    """Retrieves the list of all predictions for a patient, ordered by date desc."""
    return db.query(Prediction).filter(Prediction.patient_id == patient_id).order_by(Prediction.created_at.desc()).all()
