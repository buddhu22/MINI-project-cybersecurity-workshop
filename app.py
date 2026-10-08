from datetime import datetime
import os
from flask import Flask, jsonify, request, send_from_directory
import pandas as pd

app = Flask(__name__, static_folder="static", static_url_path="/static")

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
# Helper: Load and Validate Data
# -----------------------------

def load_and_validate():
    # SECURITY CONTROL 1 — Safe File Loading
    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        return None, "Activity log file was not found. Please contact the administrator."
    except pd.errors.EmptyDataError:
        return None, "Activity log file is empty. No data to display."
    except Exception:
        return None, "Unable to load activity logs. Please contact the administrator."

    # SECURITY CONTROL 2 — Required Column Validation
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        return None, "Activity log file is missing required fields. Please contact the administrator."

    # SECURITY CONTROL 4 — Empty Data Validation
    if df.empty:
        return None, "Activity log file contains no usable rows."

    # SECURITY CONTROL 3 — Data Type Validation
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")

    invalid_timestamps = df["timestamp"].isna().sum()
    invalid_durations = df["duration_ms"].isna().sum()

    if invalid_timestamps > 0:
        return None, f"Activity log contains {invalid_timestamps} invalid timestamp value(s). Please fix the data file."

    if invalid_durations > 0:
        return None, f"Activity log contains {invalid_durations} invalid duration value(s). Please fix the data file."

    # SECURITY CONTROL 6 — Extreme Duration Validation
    negative_durations = (df["duration_ms"] < MIN_DURATION_MS).sum()
    if negative_durations > 0:
        return None, f"Activity log contains {negative_durations} negative duration value(s). Negative durations are invalid."

    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df, None


# -----------------------------
# API Routes
# -----------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/data")
def get_data():
    df, error = load_and_validate()

    if error:
        return jsonify({"error": error}), 400

    # SECURITY CONTROL 5 — Duplicate Row Check
    duplicate_count = int(df.duplicated().sum())

    # Basic Analytics
    total_events = len(df)
    total_errors = int((df["status"] == "Error").sum())
    error_rate = round((total_errors / total_events) * 100, 2) if total_events > 0 else 0.0
    avg_duration = round(df["duration_ms"].mean(), 2) if total_events > 0 else 0.0

    # Module Analysis
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

    flagged_modules = int((module_stats["status"] == "Flagged").sum())

    # Event types & modules list for dropdowns
    event_types = ["All"] + sorted(df["event_type"].unique().tolist())
    modules = ["All"] + sorted(df["module"].unique().tolist())
    statuses = ["All"] + sorted(df["status"].unique().tolist())

    return jsonify({
        "duplicate_warning": duplicate_count,
        "metrics": {
            "total_events": total_events,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "flagged_modules": flagged_modules,
            "avg_duration": avg_duration
        },
        "activity_logs": df.to_dict(orient="records"),
        "module_stats": module_stats.to_dict(orient="records"),
        "event_types": event_types,
        "modules": modules,
        "statuses": statuses
    })


@app.route("/api/filter", methods=["GET"])
def filter_data():
    df, error = load_and_validate()
    if error:
        return jsonify({"error": error}), 400

    selected_module = request.args.get("module", "All")
    selected_status = request.args.get("status", "All")
    selected_event_type = request.args.get("event_type", "All")
    search_query = request.args.get("search", "").strip().lower()
    log_audit = request.args.get("log_audit", "false").lower() == "true"

    filtered_df = df.copy()

    if selected_module != "All":
        filtered_df = filtered_df[filtered_df["module"] == selected_module]

    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]

    if selected_event_type != "All":
        filtered_df = filtered_df[filtered_df["event_type"] == selected_event_type]

    if search_query:
        filtered_df = filtered_df[
            filtered_df["module"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["event_type"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["status"].astype(str).str.lower().str.contains(search_query) |
            filtered_df["timestamp"].astype(str).str.lower().str.contains(search_query)
        ]

    audit_record = None
    # SECURITY CONTROL 9 — Audit Logging (Triggers ONLY on explicit filter submission)
    if log_audit:
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
            pass  # Audit record could not be saved (non-fatal)

    return jsonify({
        "filtered_records": filtered_df.to_dict(orient="records"),
        "records_count": len(filtered_df),
        "audit_record": audit_record,
    })


@app.route("/api/audit")
def get_audit_logs():
    if not os.path.exists(AUDIT_FILE):
        return jsonify([])
    try:
        audit_df = pd.read_csv(AUDIT_FILE)
        return jsonify(audit_df.to_dict(orient="records"))
    except Exception:
        return jsonify([])


if __name__ == "__main__":
    app.run(debug=True, port=5050)


