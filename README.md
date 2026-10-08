# 🚀 MINI PROJECT – LAB ACTIVITY MONITOR

> **One-line explanation:**  
> *"Lab Activity Monitor ek secure analytics dashboard hai jo synthetic application activity logs ko validate aur analyze karke module-wise errors, performance aur unusual patterns ko identify aur visualize karta hai."*

---

## 📌 Project Overview

**Lab Activity Monitor** ek security-focused application activity analytics monitoring dashboard hai jo **Flask**, **Pandas**, **HTML5**, **CSS3**, aur **JavaScript (Chart.js)** se bana hai.

---

## 🔹 1. Problem Statement (Hum Log Kya Solve Kar Rahe Hain?)

Hum ek imaginary **Lab Management Application** assume kar rahe hain jisme ye core modules hain:
- 🔐 **Login**
- 📦 **Asset Management**
- 🛒 **Checkout**
- 📊 **Reports**

Application mein continuously activities perform hoti hain (jaise user login, asset searching, checkout transactions, report generation etc.).

**Problem:** Raw activity log files ko manually check karke ye determine karna bohot mushkil aur slow hota hai ki:
- Kitne overall events occur hue?
- Total kitne errors aaye?
- Kis specific module mein sabse zyada error rate hai?
- Kis module ka average response duration/latency high hai?
- Kya koi unusual/anomalous activity pattern ban raha hai?

---

## 🔹 2. Solution & Data Flow

Humne **Lab Activity Monitor** develop kiya hai jo system ke activity logs ko automatically validate, clean, analyze aur visualize karta hai.

### Final Architecture Flow:

```text
Imaginary Lab Application
        ↓
Synthetic Activity Logs
        ↓
data/activity_logs.csv
        ↓
Python + Pandas (Flask Backend)
        ↓
Read → Validate → Clean
        ↓
Analytics Computation
        ↓
Error Rate & Duration Analysis
        ↓
5% Error Threshold Detection
        ↓
HTML5 + CSS3 + JavaScript Dashboard
        ↓
Filters + Visual Charts + Flagged Modules
        ↓
data/audit_logs.csv
```

---

## 🔹 3. Activity Log Schema & Example

Primary dataset file `data/activity_logs.csv` mein ye main fields hoti hain:

- `timestamp`: Event creation date and time.
- `module`: Target module (`Login`, `Asset`, `Checkout`, `Reports`).
- `event_type`: Specific action performed.
- `status`: Result of operation (`Success` / `Error`).
- `duration_ms`: Latency duration in milliseconds.

**Example Entry:**
```text
10:05:22 → Module: Checkout → Event: Checkout → Status: Error → Duration: 850 ms
```
*Matlab Checkout module mein 10:05:22 par Checkout event hua, jo fail/error hua aur process hone mein 850 ms lage.*

---

## 🔹 4. Security Input Validation Controls

Raw CSV data ko bina verification directly dashboard mein load nahi kiya jata. Backend parsing se pehle multiple integrity checks perform hote hain:

| Control | Function |
| :--- | :--- |
| ✅ **Required Field Validation** | Ensures all essential columns (`timestamp`, `module`, `event_type`, `status`, `duration_ms`) exist. |
| ✅ **File Existence & Empty File Handling** | Missing/Empty files gracefully handled without breaking server or exposing tracebacks. |
| ✅ **Timestamp Parsing & Type Check** | Validates date formatting, filtering corrupted or invalid date strings. |
| ✅ **Numeric & Boundary Duration Check** | Enforces `duration_ms >= 0`. Rejects negative durations (physically impossible data corruption). |
| ✅ **Duplicate Entry Detection** | Identifies exact duplicate rows and raises user-facing alerts. |

---

## 🔹 5. Analytics Engine

Validation complete hone ke baad backend application-level aur module-level statistics compute karta hai:

### Overall Metrics:
- **Total Events Count**
- **Total Error Events Count**
- **Overall Application Error Rate (%)**
- **Average & Median Execution Duration (ms)**

### Module-Wise Analysis:
- Total Events & Errors per module
- Specific Module Error Rate (%)
- Module Average vs. Median Latency (ms)

---

## 🔹 6. Threshold-Based Flagging

Anomalous behavior identify karne ke liye ek threshold defined hai:

$$\text{ERROR RATE THRESHOLD} = 5.0\%$$

- Agar module ka $\text{Error Rate} > 5.0\% \implies \mathbf{FLAGGED}$
- Otherwise $\implies \mathbf{NORMAL}$

### Current Dataset Breakdown:

| Module | Total Events | Total Errors | Error Rate | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Login** | 3 | 1 | **33.33%** | 🚩 **FLAGGED** |
| **Asset** | 2 | 0 | **0.00%** | ✅ **NORMAL** |
| **Checkout** | 3 | 3 | **100.00%** | 🚩 **FLAGGED** |
| **Reports** | 2 | 0 | **0.00%** | ✅ **NORMAL** |

> ⚠️ **Important Security Clarification:**  
> `FLAGGED` status ka matlab **attack confirm hona nahi hai**.  
> Iska matlab sirf ye hai ki us module mein high/unusual error frequency hai, jiska reason application bug, database timeout, network glitch, ya bad user input bhi ho sakta hai. Deep investigation required hoti hai.

---

## 🔹 7. Web Dashboard Features

Frontend pure **HTML5**, **Vanilla CSS (Glassmorphism Dark Theme)** aur **JavaScript (Chart.js)** mein built hai:

- 📊 **Executive Overview**: Real-time KPI summary cards.
- 🚩 **Flagged Modules Banner**: Instant highlight of modules exceeding the 5% risk threshold.
- 🧩 **Module Analysis Table**: Complete breakdown of performance statistics.
- 🔎 **Log Explorer & Filters**: Dynamic filtering by Module, Event Type, Status, and instant search.
- 📈 **Interactive Visual Charts**: Chart.js charts for Error Rate distributions and Latency durations.
- 📝 **Audit Record Viewer**: Interface to view stored query filter history.

---

## 🔹 8. Privacy-First Audit Logging

Jab koi user Log Explorer par query filters apply karta hai, tab `data/audit_logs.csv` mein metadata audit record append hota hai:

- **Timestamp**
- **Module Filter**
- **Status Filter**
- **Records Found**

### Privacy Safeguards:
Audit log mein **kuchh bhi sensitive data store nahi hota**:
- ❌ No Passwords
- ❌ No API Keys or Access Tokens
- ❌ No Personal Identifiable Information (PII)
- ❌ No Real IP addresses or User Credentials

---

## 🔹 9. SSDLC & Threat Model (Security Mitigations)

| Identified Threat | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **1. Invalid / Malicious Input** | Wrong analytics calculation or app crash | Schema validation + timestamp parsing + duration boundary checks. |
| **2. Missing or Corrupted Log File** | Dashboard failure / server tracebacks | Safe file handling + user-friendly error banners. |
| **3. Sensitive Data Exposure** | Privacy violation | Synthetic data usage + minimal privacy-first audit logging. |
| **4. False Security Interpretation** | Misinterpreting operational bugs as attacks | Clear documentation & UI warning banners stating Flagged $\neq$ Attack. |

---

## 🛠️ 10. How to Run the Application

### Setup & Run Commands:

```bash
# 1. Activate Virtual Environment
myenv\Scripts\activate

# 2. Install Required Dependencies
pip install -r requirements.txt

# 3. Start the Flask Backend Server
python app.py
```

> 💡 **Note**: Always execute `python app.py` (do not run `python run app.py`).

Open browser at: `http://localhost:5050`

---

## 🌐 11. REST API Endpoints

- `GET /` : Renders the web dashboard (`static/index.html`).
- `GET /api/data` : Returns metrics, module statistics, raw activity logs, and filter dropdown options.
- `GET /api/filter` : Returns filtered log records and logs search metadata to `data/audit_logs.csv`.
- `GET /api/audit` : Retrieves history of query audit records.

---

## 🧠 Simple Memory Formula

$$\text{RAW LOGS} \longrightarrow \text{VALIDATE} \longrightarrow \text{ANALYZE} \longrightarrow \text{FLAG} \longrightarrow \text{VISUALIZE} \longrightarrow \text{INVESTIGATE} \longrightarrow \text{AUDIT}$$
