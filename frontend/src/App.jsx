import { useState, useEffect, useRef } from 'react'

const API_URL = 'http://localhost:8000';

// ─── Professional SVG Icons ─────────────────────────────────────────────────
const Icons = {
  heartPulse: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
      <path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>
    </svg>
  ),
  stethoscope: (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/>
      <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/>
      <circle cx="20" cy="10" r="2"/>
    </svg>
  ),
  user: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  ),
  signOut: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  ),
  search: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <path d="m21 21-4.3-4.3"/>
    </svg>
  ),
  activity: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>
    </svg>
  ),
  barChart: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="16"/>
    </svg>
  ),
  brain: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
      <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
      <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
      <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>
      <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/>
      <path d="M3.477 10.896a4 4 0 0 1 .585-.396"/>
      <path d="M19.938 10.5a4 4 0 0 1 .585.396"/>
      <path d="M6 18a4 4 0 0 1-1.967-.516"/>
      <path d="M19.967 17.484A4 4 0 0 1 18 18"/>
    </svg>
  ),
  clock: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  upload: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/>
      <line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  alertCircle: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  checkCircle: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  play: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polygon points="10 8 16 12 10 16 10 8"/>
    </svg>
  ),
  loader: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
    </svg>
  ),
  fileText: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
      <path d="M14 2v4a2 2 0 0 0 2 2h4"/>
      <line x1="10" y1="9" x2="10" y2="9.01"/>
      <line x1="10" y1="13" x2="14" y2="13"/>
      <line x1="10" y1="17" x2="14" y2="17"/>
    </svg>
  ),
  plus: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  ),
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) {
      const parts = dateStr.split('T');
      if (parts.length > 0) return parts[0]; 
      return 'Invalid';
    }
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return 'N/A';
  }
};

const CLASS_LABELS = {
  'N': 'Normal Beat',
  'A': 'Atrial Premature Beat',
  'V': 'Premature Ventricular Contraction',
  'L': 'Left Bundle Branch Block Beat',
  'R': 'Right Bundle Branch Block Beat'
};

function App() {
  // Auth state
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [doctorName, setDoctorName] = useState(localStorage.getItem('doctorName') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  // Dashboard state
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientHistory, setPatientHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  // Analysis / input state
  const [patientName, setPatientName] = useState('');
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('Male');
  const [ecgSignalStr, setEcgSignalStr] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState('');

  // active prediction result
  const [activeResult, setActiveResult] = useState(null);

  // Sync token to localStorage
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('doctorName', doctorName);
      loadPatients();
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('doctorName');
      setPatients([]);
      setSelectedPatient(null);
      setPatientHistory([]);
    }
  }, [token]);



  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result;
      const cleanStr = content.replace(/[\[\]]/g, '');
      const separators = /[\s,;\n\t\r]+/;
      const parsedValues = cleanStr
        .split(separators)
        .map(v => v.trim())
        .filter(v => v !== '')
        .map(parseFloat);
        
      if (parsedValues.length === 187 && !parsedValues.some(isNaN)) {
        setEcgSignalStr(parsedValues.join(', '));
        setAnalysisError('');
      } else {
        setAnalysisError(`Invalid file format: found ${parsedValues.length} numeric values. The signal must contain exactly 187 numbers.`);
      }
    };
    reader.onerror = () => {
      setAnalysisError('Error reading file.');
    };
    reader.readAsText(file);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Incorrect credentials');
      }
      const data = await res.json();
      setDoctorName(data.doctor_name);
      setToken(data.access_token);
    } catch (err) {
      setLoginError(err.message);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setDoctorName('');
  };

  const loadPatients = async () => {
    try {
      const res = await fetch(`${API_URL}/patients`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPatients(data);
      }
    } catch (err) {
      console.error("Error loading patients:", err);
    }
  };

  const selectPatient = async (patient) => {
    setSelectedPatient(patient);
    setPatientName(patient.name);
    setPatientAge(patient.age || '');
    setPatientGender(patient.gender || 'Male');
    setActiveResult(null);
    
    // Load patient history
    try {
      const res = await fetch(`${API_URL}/patients/${patient.id}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPatientHistory(data);
        if (data.length > 0) {
          // Set latest prediction as active result
          setActiveResult(data[0]);
        }
      }
    } catch (err) {
      console.error("Error loading patient history:", err);
    }
  };

  const handleNewAnalysis = () => {
    setSelectedPatient(null);
    setPatientName('');
    setPatientAge('');
    setPatientGender('Male');
    setActiveResult(null);
    setPatientHistory([]);
    setEcgSignalStr('');
  };

  const runAnalysis = async (e) => {
    e.preventDefault();
    setAnalysisError('');
    if (!patientName.trim()) {
      setAnalysisError('Patient name is required.');
      return;
    }
    
    // Parse signal array
    const cleanStr = ecgSignalStr.replace(/[\[\]]/g, '');
    const signal = cleanStr.split(',').map(s => parseFloat(s.trim()));
    if (signal.length !== 187 || signal.some(isNaN)) {
      setAnalysisError('ECG signal must contain exactly 187 numeric comma-separated values.');
      return;
    }

    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          patient_name: patientName,
          patient_age: patientAge ? parseInt(patientAge) : null,
          patient_gender: patientGender,
          signal: signal
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Prediction failed');
      }
      const data = await res.json();
      setActiveResult(data);
      
      // Reload patients list to catch newly created patient
      await loadPatients();
      
      // Find the patient in the updated list and select them to show their updated history
      const patientRes = await fetch(`${API_URL}/patients/${data.patient_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (patientRes.ok) {
        const patientData = await patientRes.json();
        setSelectedPatient(patientData);
        // Reload history
        const histRes = await fetch(`${API_URL}/patients/${data.patient_id}/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (histRes.ok) {
          const histData = await histRes.json();
          setPatientHistory(histData);
        }
      }
      
    } catch (err) {
      setAnalysisError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Filter patients list based on search bar
  const filteredPatients = patients.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Parse signal string into array for rendering the SVG graph
  const getEcgPoints = () => {
    try {
      const cleanStr = ecgSignalStr.replace(/[\[\]]/g, '');
      const signal = cleanStr.split(',').map(s => parseFloat(s.trim()));
      if (signal.length === 0 || signal.some(isNaN)) return [];
      
      const width = 800;
      const height = 130;
      const step = width / (signal.length - 1);
      
      return signal.map((val, idx) => {
        const x = idx * step;
        // Invert Y axis for canvas coordinates (0 is top, 130 is bottom)
        // Center the wave vertically and scale it
        const y = 15 + (1 - val) * 100; 
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(' ');
    } catch (err) {
      return '';
    }
  };

  const ecgPointsStr = getEcgPoints();

  // Get status color based on prediction class
  const getStatusColor = (cls) => {
    if (cls === 'N') return 'normal';
    if (cls === 'A' || cls === 'L' || cls === 'R') return 'warning';
    return 'critical';
  };

  const getStatusBadge = (cls) => {
    if (cls === 'N') return 'badge-normal';
    if (cls === 'A' || cls === 'L' || cls === 'R') return 'badge-warning';
    return 'badge-abnormal';
  };

  // Render Login view
  if (!token) {
    return (
      <div className="login-wrapper">
        <div className="login-card glass-panel glow-on-hover">
          <div className="login-header">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '6px', color: 'var(--primary)' }}>
              {Icons.heartPulse}
            </div>
            <h1>Cardio<span className="brand-accent">Diffusion</span></h1>
            <p>Clinical ECG Diffusion & Diagnostics Portal</p>
          </div>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Username</label>
              <input 
                type="text" 
                className="input-control" 
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input 
                type="password" 
                className="input-control" 
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" style={{ marginTop: '10px' }}>
              Sign In
            </button>
            {loginError && (
              <div className="error-message">
                {Icons.alertCircle}
                <span>{loginError}</span>
              </div>
            )}
          </form>
          <div className="credentials-box">
            <div className="cred-title">Demo Credentials</div>
            <div className="cred-item">Username: <code>doctor1</code> &middot; Password: <code>password123</code></div>
            <div className="cred-item">Username: <code>doctor2</code> &middot; Password: <code>password123</code></div>
          </div>
        </div>
      </div>
    );
  }

  // Render Dashboard view
  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-text">
            <span className="logo-icon">{Icons.heartPulse}</span>
            Cardio<span className="brand-accent">Diffusion</span>
          </div>
          <div className="doctor-profile">
            <div className="doctor-avatar">
              {doctorName ? doctorName.replace('Dr. ', '').substring(0, 2).toUpperCase() : 'DR'}
            </div>
            <div className="doctor-info">
              <h4>{doctorName}</h4>
              <span>Cardiologist</span>
            </div>
            <button className="logout-btn" title="Sign Out" onClick={handleLogout}>
              {Icons.signOut}
            </button>
          </div>
        </div>

        <div className="patient-search-box">
          <div className="search-input-wrapper">
            <span className="search-icon">{Icons.search}</span>
            <input 
              type="text" 
              className="input-control" 
              placeholder="Search patients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="patient-list">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3>Patients</h3>
            <button 
              onClick={handleNewAnalysis}
              className="btn-new-analysis"
            >
              {Icons.plus} New Analysis
            </button>
          </div>
          {filteredPatients.length === 0 ? (
            <div style={{ padding: '20px 8px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No patients found.
            </div>
          ) : (
            filteredPatients.map(p => (
              <div 
                key={p.id} 
                className={`patient-item ${selectedPatient && selectedPatient.id === p.id ? 'active' : ''}`}
                onClick={() => selectPatient(p)}
              >
                <div className="patient-icon">{Icons.user}</div>
                <div className="patient-meta">
                  <h4>{p.name}</h4>
                  <span>{p.age ? `${p.age} y/o` : 'Age N/A'} &middot; {p.gender || 'Gender N/A'}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Panel */}
      <main className="main-content">
        <div className="dashboard-header">
          <div>
            <h1>ECG Diagnostic Workspace</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
              {selectedPatient ? `Viewing records for patient: ${selectedPatient.name}` : 'Configure a new patient diagnostic run'}
            </p>
          </div>
          {selectedPatient && (
            <button 
              className="btn-primary" 
              style={{ width: 'auto', padding: '10px 20px', fontSize: '0.88rem', display: 'inline-flex', alignItems: 'center', gap: '8px' }}
              onClick={handleNewAnalysis}
            >
              {Icons.plus} Analyze New Patient
            </button>
          )}
        </div>

        <div className="dashboard-grid">
          {/* Left Hand: ECG input & signal drawing */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="glass-panel analysis-card">
              <h2 className="section-title">
                <span className="section-icon">{Icons.activity}</span>
                ECG Signal Input & Parameters
              </h2>
              <form onSubmit={runAnalysis}>
                <div className="form-row">
                  <div className="form-group">
                    <label>Patient Name</label>
                    <input 
                      type="text" 
                      className="input-control" 
                      placeholder="e.g. John Doe"
                      value={patientName}
                      onChange={(e) => setPatientName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Age</label>
                    <input 
                      type="number" 
                      className="input-control" 
                      placeholder="e.g. 45"
                      value={patientAge}
                      onChange={(e) => setPatientAge(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Gender</label>
                    <select 
                      className="input-control"
                      value={patientGender}
                      onChange={(e) => setPatientGender(e.target.value)}
                      style={{ background: 'var(--bg-panel-solid)' }}
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>



                {/* File Upload Option for Real Examples */}
                <div className="file-upload-area">
                  <div className="file-upload-label">
                    Load Real ECG Signal Data
                  </div>
                  <div className="file-upload-row">
                    <input 
                      type="file" 
                      accept=".txt,.csv" 
                      onChange={handleFileUpload} 
                      className="input-control" 
                      style={{ display: 'none' }}
                      id="signal-file-upload"
                    />
                    <label 
                      htmlFor="signal-file-upload" 
                      className="btn-upload"
                    >
                      {Icons.upload} Upload ECG File (.csv, .txt)
                    </label>
                    <span className={`file-upload-status ${ecgSignalStr ? 'loaded' : ''}`}>
                      {ecgSignalStr ? (
                        <>{Icons.checkCircle} ECG data loaded successfully</>
                      ) : (
                        'Upload a text file containing exactly 187 numbers'
                      )}
                    </span>
                  </div>
                </div>

                {/* SVG wave drawing */}
                {ecgPointsStr && (
                  <div className="ecg-graph-wrapper">
                    <div className="ecg-graph-grid"></div>
                    <svg className="ecg-svg" viewBox="0 0 800 130" preserveAspectRatio="none">
                      <polyline className="ecg-path" points={ecgPointsStr} />
                    </svg>
                  </div>
                )}

                <div className="signal-input-group">
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    ECG Raw Signals (187 normalized floats)
                  </label>
                  <textarea 
                    className="input-control signal-textarea"
                    placeholder="Enter 187 numbers separated by commas..."
                    value={ecgSignalStr}
                    onChange={(e) => setEcgSignalStr(e.target.value)}
                    required
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn-primary" 
                  disabled={isAnalyzing}
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                >
                  {isAnalyzing ? (
                    <><span className="spinner-icon">{Icons.loader}</span> Analyzing via Diffusion Classifier...</>
                  ) : (
                    <>{Icons.play} Run Diagnostic Classifier & Generate Report</>
                  )}
                </button>
                {analysisError && (
                  <div className="error-message">
                    {Icons.alertCircle}
                    <span>{analysisError}</span>
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* Right Hand: Prediction result & explanation */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {activeResult ? (
              <>
                <div className="glass-panel result-card">
                  <h2 className="section-title">
                    <span className="section-icon">{Icons.barChart}</span>
                    Diagnostic Assessment
                  </h2>
                  <div className="result-header">
                    <div className={`diagnosis-badge ${getStatusBadge(activeResult.predicted_class)}`}>
                      <span className={`pulse-light pulse-${getStatusColor(activeResult.predicted_class)}`}></span>
                      {CLASS_LABELS[activeResult.predicted_class] || activeResult.predicted_class}
                    </div>
                    <div className="confidence-metric">
                      <div className="confidence-val">{(activeResult.confidence * 100).toFixed(1)}%</div>
                      <div className="confidence-lbl">Confidence</div>
                    </div>
                  </div>

                  <div className="progress-container">
                    <div 
                      className="progress-bar" 
                      style={{ 
                        width: `${activeResult.confidence * 100}%`,
                        backgroundColor: `var(--accent-${getStatusColor(activeResult.predicted_class) === 'normal' ? 'green' : getStatusColor(activeResult.predicted_class) === 'warning' ? 'orange' : 'red'})`
                      }}
                    ></div>
                  </div>

                  {activeResult.probabilities && (
                    <div className="probabilities-list">
                      {Object.entries(activeResult.probabilities).map(([cls, prob]) => (
                        <div key={cls} className="prob-item">
                          <div className="prob-header">
                            <span className="prob-name">{CLASS_LABELS[cls] || cls} ({cls})</span>
                            <span className="prob-val">{(prob * 100).toFixed(1)}%</span>
                          </div>
                          <div className="prob-track">
                            <div className="prob-bar" style={{ width: `${prob * 100}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeResult.explanation && (
                    <div className="explanation-box">
                      <div className="explanation-title">
                        <span className="section-icon">{Icons.brain}</span>
                        AI Clinical Interpretation Notes
                      </div>
                      <div className="explanation-text">
                        {activeResult.explanation.split('\n\n').map((para, pIdx) => (
                          <p key={pIdx}>{para}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Patient History logs */}
                {selectedPatient && patientHistory.length > 0 && (
                  <div className="glass-panel history-card">
                    <h2 className="section-title">
                      <span className="section-icon">{Icons.clock}</span>
                      Diagnostic History
                    </h2>
                    <div className="history-timeline">
                      {patientHistory.map((hist) => (
                        <div 
                          key={hist.id} 
                          className="history-item"
                          onClick={() => setActiveResult(hist)}
                          style={{
                            borderColor: activeResult.id === hist.id ? 'var(--primary)' : 'var(--border)'
                          }}
                        >
                          <div 
                            className="history-dot" 
                            style={{ 
                              backgroundColor: `var(--accent-${getStatusColor(hist.predicted_class) === 'normal' ? 'green' : getStatusColor(hist.predicted_class) === 'warning' ? 'orange' : 'red'})` 
                            }}
                          ></div>
                          <div className="history-item-details">
                            <div className="history-item-header">
                              <span className="history-item-class">{CLASS_LABELS[hist.predicted_class] || hist.predicted_class}</span>
                              <span className="history-item-time">{formatDate(hist.created_at)}</span>
                            </div>
                            <div className="history-item-meta">
                              Confidence: {(hist.confidence * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="no-selection glass-panel">
                <div className="no-selection-icon">{Icons.stethoscope}</div>
                <h3>No Diagnostic Run Selected</h3>
                <p style={{ marginTop: '8px', fontSize: '0.88rem' }}>
                  Please load a patient or analyze an ECG signal to populate the diagnostic report.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
