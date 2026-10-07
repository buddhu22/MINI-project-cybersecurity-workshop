from datetime import datetime
import os
import streamlit as st
import pandas as pd

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Lab Activity Monitor",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Constants
# -----------------------------

FILE_PATH = "data/activity_logs.csv"
AUDIT_FILE = "data/audit_logs.csv"

REQUIRED_COLUMNS = [
    "timestamp",
    "module",
    "event_type",
    "status",
    "duration_ms",
]

# Duration validation rule:
# Negative durations are physically impossible.
# We reject them as data corruption or bad input.
# No upper bound is enforced — large but positive values may be valid.
MIN_DURATION_MS = 0

ERROR_RATE_THRESHOLD = 5.0

# -----------------------------
# SECURITY CONTROL 1 — Safe File Loading
# -----------------------------
# All error messages are safe: no raw tracebacks are exposed to the user.

try:
    df = pd.read_csv(FILE_PATH)

except FileNotFoundError:
    st.error("Activity log file was not found. Please contact the administrator.")
    st.stop()

except pd.errors.EmptyDataError:
    st.error("Activity log file is empty. No data to display.")
    st.stop()

except Exception:
    st.error("Unable to load activity logs. Please contact the administrator.")
    st.stop()

# -----------------------------
# SECURITY CONTROL 2 — Required Column Validation
# -----------------------------

missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

if missing_columns:
    st.error("Activity log file is missing required fields. Please contact the administrator.")
    st.stop()

# -----------------------------
# SECURITY CONTROL 4 — Empty Data Validation
# -----------------------------

if df.empty:
    st.error("Activity log file contains no usable rows.")
    st.stop()

# -----------------------------
# SECURITY CONTROL 3 — Data Type Validation
# -----------------------------

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")

invalid_timestamps = df["timestamp"].isna().sum()
invalid_durations = df["duration_ms"].isna().sum()

if invalid_timestamps > 0:
    st.error(f"Activity log contains {invalid_timestamps} invalid timestamp value(s). Please fix the data file.")
    st.stop()

if invalid_durations > 0:
    st.error(f"Activity log contains {invalid_durations} invalid duration value(s). Please fix the data file.")
    st.stop()

# -----------------------------
# SECURITY CONTROL 6 — Extreme Duration Validation
# -----------------------------
# Reject negative durations — they are physically impossible and indicate
# corrupted or tampered data. Large positive values are kept as-is.

negative_durations = (df["duration_ms"] < MIN_DURATION_MS).sum()

if negative_durations > 0:
    st.error(f"Activity log contains {negative_durations} negative duration value(s). Negative durations are invalid.")
    st.stop()

# -----------------------------
# SECURITY CONTROL 5 — Duplicate Row Check
# -----------------------------
# Warn if duplicates exist but do not crash or expose sensitive details.

duplicate_count = df.duplicated().sum()

if duplicate_count > 0:
    st.warning(f"Warning: {duplicate_count} duplicate row(s) detected in the activity log.")

# -----------------------------
# Basic Analytics
# -----------------------------

total_events = len(df)
total_errors = (df["status"] == "Error").sum()
error_rate = (total_errors / total_events) * 100

# Flagged modules = modules whose error rate exceeds threshold
# (computed properly below after module_stats is built)

# -----------------------------
# Dashboard Title
# -----------------------------

st.title("📊 Lab Activity Monitor")
st.write("Application Activity Analytics Dashboard")

# -----------------------------
# Module Analysis (computed early for flagged_modules metric)
# -----------------------------

module_stats = (
    df.groupby("module")
      .agg(
          total_events=("status", "size"),
          total_errors=("status", lambda x: (x == "Error").sum()),
          average_duration_ms=("duration_ms", "mean"),
          median_duration_ms=("duration_ms", "median")
      )
      .reset_index()
)

module_stats["error_rate"] = (
    module_stats["total_errors"] / module_stats["total_events"]
) * 100

module_stats["error_rate"] = module_stats["error_rate"].round(2)
module_stats["average_duration_ms"] = module_stats["average_duration_ms"].round(2)
module_stats["median_duration_ms"] = module_stats["median_duration_ms"].round(2)

module_stats["status"] = module_stats["error_rate"].apply(
    lambda rate: "Flagged" if rate > ERROR_RATE_THRESHOLD else "Normal"
)

flagged_modules = (module_stats["status"] == "Flagged").sum()

# -----------------------------
# Metrics
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Events", total_events)

with col2:
    st.metric("Total Errors", int(total_errors))

with col3:
    st.metric("Error Rate", f"{error_rate:.2f}%")

with col4:
    st.metric("Flagged Modules", int(flagged_modules))

# -----------------------------
# Activity Logs
# -----------------------------

st.subheader("Activity Logs")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Module Analysis
# -----------------------------

st.subheader("Module Analysis")
st.dataframe(module_stats, use_container_width=True)

# -----------------------------
# Log Explorer
# -----------------------------

st.subheader("🔎 Log Explorer")

# Module filter
modules = ["All"] + sorted(df["module"].unique().tolist())
selected_module = st.selectbox("Select Module", modules)

# Status filter
statuses = ["All"] + sorted(df["status"].unique().tolist())
selected_status = st.selectbox("Select Status", statuses)

# Apply filters
filtered_df = df.copy()

if selected_module != "All":
    filtered_df = filtered_df[filtered_df["module"] == selected_module]

if selected_status != "All":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]

st.write("Filtered Records:", len(filtered_df))
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# Analytics Charts
# -----------------------------

st.subheader("📊 Analytics")

st.write("### Module-wise Error Rate")
error_rate_chart = module_stats[["module", "error_rate"]].set_index("module")
st.bar_chart(error_rate_chart)

st.write("### Module-wise Average Duration")
duration_chart = module_stats[["module", "average_duration_ms"]].set_index("module")
st.bar_chart(duration_chart)

# -----------------------------
# SECURITY CONTROL 9 — Audit Logging
# -----------------------------
# Only safe, non-sensitive fields are stored:
# timestamp, module_filter, status_filter, records_found.
# No raw activity records or personal data are written.

audit_record = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "module_filter": selected_module,
    "status_filter": selected_status,
    "records_found": len(filtered_df),
}

audit_df = pd.DataFrame([audit_record])

try:
    if os.path.exists(AUDIT_FILE):
        audit_df.to_csv(AUDIT_FILE, mode="a", header=False, index=False)
    else:
        audit_df.to_csv(AUDIT_FILE, index=False)
except Exception:
    st.warning("Audit record could not be saved.")

st.subheader("📝 Audit Record")
st.dataframe(audit_df, use_container_width=True)