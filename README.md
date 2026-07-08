# CardioDiffusion

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat&logo=react)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=flat&logo=pytorch)](https://pytorch.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Core-black)](https://github.com/langchain-ai/langchain)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model%20Repository-orange)](https://huggingface.co/Abderrahmen7/cardiodiffusion-ecg-classifier)

An enterprise-grade Clinical ECG Diagnostics & Diagnostics Portal. CardioDiffusion leverages a custom 1D CNN + BiLSTM deep learning model to classify ECG signals alongside a LLaMA-based Large Language Model (LLM) interpreter (via LangChain & Groq) to generate clear, medically contextualized interpretative notes for cardiologists and clinical staff.

---

## ⚡ System Architecture

The application comprises three core components:

```mermaid
graph TD
    A[React Client Web App] -->|HTTPS Requests + Bearer JWT| B[FastAPI Backend Gateway]
    B -->|Database Operations| C[(SQLAlchemy DB - SQLite/PostgreSQL)]
    B -->|Signal Classification| D[PyTorch CNN-BiLSTM Engine]
    B -->|Clinical Note Synthesis| E[LangChain + Groq LLaMA-3.3-70B API]
```

1. **Analytical Deep Learning Classifier (PyTorch)**: Implements a 1D Convolutional Neural Network (CNN) combined with a Bidirectional LSTM (BiLSTM) network to ingest 187-point normalized ECG float signals and accurately categorize arrhythmias.
2. **Generative LLM Interpretation Engine (LangChain + Groq)**: Synthesizes probability outputs and structural class features into professional clinical notes using `llama-3.3-70b-versatile` with low latency.
3. **Clinical Workspace Application**: Developed with React and FastAPI, styled with a modern clinical theme for high-stress diagnostics environments.

---

## 🚀 Core Features

- **Arrhythmia Classification**: Deep-learning classification of five distinct cardiac categories:
  - `N`: Normal Sinus Rhythm
  - `A`: Atrial Premature Beat (APB)
  - `V`: Premature Ventricular Contraction (PVC)
  - `L`: Left Bundle Branch Block Beat (LBBB)
  - `R`: Right Bundle Branch Block Beat (RBBB)
- **Clinical Explanations**: Generates professional explanations for patients and physicians.
- **Diagnostics Records & Patient Timelines**: Real-time management of patients and historical diagnostics.
- **Real ECG Upload Pipeline**: Direct loading of real ECG readings via plain `.txt` or `.csv` files.
- **Themed UI**: Professional clinical theme leveraging the highly legible **Inter** font family and clean SVG iconography.
- **Physician Authentication**: Registration and secure authentication using PBKDF2 password hashing and JSON Web Tokens (JWT).

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Asynchronous Gateway)
- **Database Engine**: SQLAlchemy 2.0 ORM with native SQLite / PostgreSQL (`psycopg` v3 driver) support
- **ML Inference**: PyTorch (`torch`), NumPy
- **Generative AI**: LangChain-core, `langchain-groq` (Groq Cloud API integration)

### Frontend
- **Bundler & Tooling**: Vite + React
- **Typography**: Inter (optimized for text readability & clinical interfaces)
- **Design Language**: Vanilla CSS (glassmorphism variables, dark slate primary palette, responsive grids)
- **Iconography**: Inline vector SVGs (optimized for scaling & rendering performance)

---

## 📂 Project Directory Structure

```text
├── backend/                   # FastAPI Server Root
│   ├── main.py                # Router definitions & Gateway setup
│   ├── database.py            # SQLAlchemy config, ORM models, DB helpers
│   ├── auth.py                # PBKDF2 Hashing, JWT encode/decode logic
│   ├── model.py               # 1D CNN-BiLSTM PyTorch model definition
│   └── llm.py                 # LangChain Groq LLM clinical notes synthesis
├── frontend/                  # React Frontend Workspace
│   ├── public/                # Static public assets
│   ├── src/
│   │   ├── App.jsx            # Main React application shell & UI logic
│   │   ├── index.css          # Clinical design system & stylesheet
│   │   └── main.jsx           # App bootstrap entry
│   ├── index.html             # HTML Shell
│   ├── vite.config.js         # Vite configuration
│   └── package.json           # Frontend dependency manifest
├── models/                    # Model Storage Directory
│   └── cnn_model.pth          # Saved PyTorch weights file (Available on Hugging Face: Abderrahmen7/cardiodiffusion-ecg-classifier)
├── requirements.txt           # Python dependency specifications
└── README.md                  # System Documentation
```

---

## 📥 Setup & Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18.x or higher
- A Groq API Key (Sign up at [Groq Console](https://console.groq.com/))

### 1. Backend API Configuration

1. Navigate to the root directory and create a `.env` file:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   DATABASE_URL=sqlite:///./cardio_diffusion.db # Or postgresql+psycopg://user:password@localhost:5432/dbname
   JWT_SECRET=your_custom_secret_key_here
   ```

2. Set up a Python virtual environment and install dependencies:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. Launch the Uvicorn server:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

---

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node packages and boot the hot-reloading development server:
   ```bash
   npm install
   npm run dev
   ```

3. Access the portal in your browser at `http://localhost:5173`.

---

## 📡 API Reference

### Authentication Endpoints

| Endpoint | Method | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `/signup` | `POST` | `SignupRequest` | Registers a new doctor account and returns a Bearer token |
| `/login` | `POST` | `LoginRequest` | Verifies credentials and returns a Session Bearer token |
| `/me` | `GET` | *None* | Retrieves metadata of the authenticated doctor |

### Patient & Diagnostics Endpoints (Authenticated)

| Endpoint | Method | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `/patients` | `GET` | *None* | Fetches all patients assigned to the active doctor |
| `/patients` | `POST` | `PatientCreate` | Creates a new patient record |
| `/patients/{id}` | `GET` | *None* | Fetches a single patient profile |
| `/patients/{id}` | `DELETE` | *None* | Deletes a patient and cascades deletions to all history records |
| `/predict` | `POST` | `PredictByNameRequest` | Classifies raw ECG signal, updates patient, returns model output |
| `/patients/{id}/predict` | `POST` | `PredictRequest` | Evaluates a raw ECG signal for an existing patient ID |
| `/patients/{id}/history` | `GET` | *None* | Returns a historical list of classification runs for the patient |

---

## 🔒 Security & Data Integrity

- **Cryptographic Protections**: Password records are protected with custom salt-appended **PBKDF2 with SHA-256** hash generation (100,000 iterations).
- **Session Security**: JWT Bearer verification prevents access to resources unless authenticated.
- **Relational Constraints**: Deleting patients triggers database-level cascades to instantly clean up linked diagnostic runs and prediction JSON data.

---

## 📄 License
This project is proprietary and intended for clinical research evaluation. All classification scores and suggestions are AI-generated and should not substitute human clinical validation.