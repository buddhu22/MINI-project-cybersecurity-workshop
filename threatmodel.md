# Threat Model — Lab Activity Monitor

## 1. Invalid or Malicious Input

### Threat
Activity logs may contain invalid timestamps,
invalid durations, or missing required fields.

### Impact
Incorrect analytics or application failure.

### Mitigation
- Required-column validation
- Timestamp validation
- Duration validation
- Safe error handling

---

## 2. Missing or Empty Log File

### Threat
The activity log file may be missing or empty.

### Impact
Dashboard may fail or expose internal errors.

### Mitigation
- File existence handling
- Empty file handling
- Safe Streamlit error messages
- Stop execution using st.stop()

---

## 3. Sensitive Data Exposure

### Threat
Sensitive information could accidentally be stored
in activity logs or audit records.

### Impact
Confidential information could be exposed.

### Mitigation
- Use synthetic data only
- Do not store passwords, API keys, tokens,
  or personal information
- Keep audit records minimal

---

## 4. False Security Interpretation

### Threat
A flagged module may incorrectly be interpreted as
proof of an attack.

### Impact
False security conclusions.

### Mitigation
A flagged module represents an unusual/high error
pattern and is not proof of an attack.

Further investigation would be required.