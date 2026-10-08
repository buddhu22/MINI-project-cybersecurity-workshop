# 🛡️ Lab Activity Monitor — Security Analytics Dashboard

A security-focused application activity analytics and security monitoring dashboard built with **Flask**, **Pandas**, and modern **HTML5/CSS3/JavaScript (Chart.js)**. 

The application ingests synthetic system activity logs, performs schema and data integrity validations, computes module-level error rates and performance metrics, and flags high-risk modules based on predefined security thresholds.

---

## 📌 1. Project Overview

**Lab Activity Monitor** processes system event logs from a simulated Lab Management Application. It provides real-time security analytics, telemetry metrics, interactive charts, and audit logging to help security analysts detect anomalous module error spikes.

### Key Metrics Monitored
- **Total Event Volume & Error Count**
- **Overall Application Error Rate (%)**
- **Average & Median Event Latency (ms)**
- **Threshold-based Flagged Modules** (> 5% Error Rate)
- **Duplicate Record Detection**

> ℹ️ **Security Note:** A "Flagged" status indicates an abnormal error frequency requiring administrator investigation. It is a monitoring alert, **not** definitive proof of an active cyber attack.

---

## 🚀 2. Features

- **Executive Overview Dashboard**: Real-time KPI summary cards.
- **Module Error Analysis**: Automatic classification of system modules into `Normal` or `Flagged` status based on a 5.0% error threshold.
- **Interactive Log Explorer**: Dynamic multi-criteria filtering (Module, Event Type, Status) and instant keyword searching.
- **Analytics Visualizations**: Interactive Chart.js charts displaying module error distributions and average execution durations.
- **Privacy-First Audit Logging**: Automatic, non-sensitive audit records generated upon explicit log filtering queries (`data/audit_logs.csv`).
- **Robust Security & Validation**: Backend guards against missing columns, malformed timestamps, empty CSVs, corrupt types, and negative durations.

---

## 🏗️ 3. Architecture & Data Flow

```
┌──────────────────────────────────┐
│   Simulated Lab Application      │
│ (Login | Asset | Checkout | Rpt) │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│     Synthetic Activity Logs      │
│     (data/activity_logs.csv)     │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│      Flask Backend (app.py)      │
│  - File Integrity & Type Checks  │
│  - Duration Boundary Validation   │
│  - Pandas Analytics Computation  │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│      REST API Endpoints          │
│  /api/data  |  /api/filter       │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│    Frontend Dashboard UI         │
│  (HTML5 / Vanilla CSS / JS)      │
│  - KPI Cards | Charts | Tables   │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│      Audit Log Storage           │
│      (data/audit_logs.csv)       │
└──────────────────────────────────┘
```

---

## 📁 4. Project Structure

```text
Mini Project workshop/
├── app.py                  # Flask Backend Server & REST APIs
├── app.ipynb               # Data Exploration & Analytics Notebook
├── threatmodel.md          # Threat Model & Security Mitigations
├── requirements.txt        # Python Dependencies (Flask, Pandas, NumPy)
├── README.md               # Project Documentation
├── data/
│   ├── activity_logs.csv   # Primary System Activity Log Dataset
│   └── audit_logs.csv      # Audit Trail Records
├── static/                 # Frontend Web Assets
│   ├── index.html          # Web Dashboard Interface
│   ├── style.css           # Glassmorphic Dark UI Stylesheet
│   └── dashboard.js        # Dynamic UI Logic & Chart.js Integration
└── tests/                  # Test Suite Directory
```

---

## 🔒 5. Security & Input Validation Controls

| Security Control | Description |
| :--- | :--- |
| **1. Safe File Loading** | Graceful exception handling for missing, corrupted, or unreadable log files without exposing stack traces. |
| **2. Schema Validation** | Validates presence of required fields (`timestamp`, `module`, `event_type`, `status`, `duration_ms`). |
| **3. Data Type Coercion** | Parses ISO timestamps and numeric values, rejecting invalid datetime strings or corrupt fields. |
| **4. Boundary Enforcement** | Enforces `duration_ms >= 0`. Rejects physically impossible negative durations. |
| **5. Duplicate Detection** | Scans for duplicate log rows and flags warnings to dashboard users. |
| **6. Privacy Audit Logging**| Stores minimal metadata (timestamp & search filter criteria). **No sensitive data** (passwords, PII, keys) is recorded. |

---

## 🛠️ 6. Installation & How to Run

### Prerequisites
- Python 3.9+
- Virtual environment (`venv`)

### Setup Instructions

1. **Clone the repository** (if not already local):
   ```bash
   git clone https://github.com/buddhu22/MINI-project-cybersecurity-workshop.git
   cd "MINI-project-cybersecurity-workshop"
   ```

2. **Create & Activate Virtual Environment**:
   - **Windows (PowerShell / Command Prompt)**:
     ```bash
     python -m venv myenv
     myenv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv myenv
     source myenv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   > 💡 **Note**: Make sure to run `python app.py` (do not use `python run app.py`).

5. **Access the Dashboard**:
   Open your browser and navigate to:
   ```text
   http://localhost:5050
   ```

---

## 🌐 7. REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | Serves the main HTML5 dashboard interface. |
| `GET /api/data` | `GET` | Returns validate activity metrics, module breakdown, filter dropdown values, and raw logs. |
| `GET /api/filter` | `GET` | Filters logs by `module`, `status`, `event_type`, and `search` query. Appends an entry to `audit_logs.csv` if `log_audit=true`. |
| `GET /api/audit` | `GET` | Retrieves recorded audit logs from `data/audit_logs.csv`. |

---

## 🧪 8. Data Validation & Testing

The backend validates incoming activity logs against several corruption edge cases:
- Missing log file
- Empty log CSV file
- Missing required header columns
- Invalid timestamp strings
- Non-numeric or negative duration values
- Duplicate record entries

Refer to [`threatmodel.md`](threatmodel.md) for full threat modeling, risk assessments, and mitigation strategies.

---

## 📝 9. Limitations & Future Scope

- **Synthetic Logs**: Uses simulated data for demonstration and security educational purposes.
- **Threshold Rule**: Simple 5% error rate flagging (can produce false positives in low-volume modules).
- **Future Enhancements**:
  - Integration with real SIEM/Syslog feeds.
  - Role-Based Access Control (RBAC) & OAuth2 authentication.
  - Anomaly detection using Machine Learning (Isolation Forests).
  - Webhook/Slack alert integrations.

---

## 📄 License & Attribution

Developed for the **Cybersecurity Workshop 2026**. Educational and security analytics project.
