
import json
import os
from datetime import datetime

LOG_FILE = "logs/usage_log.json"

def log_usage(
    source: str,
    action: str,
    user: str,
    query: str,
    records_returned: int,
    status: str = "success"
):
    """
    Log every data access event with full metadata.
    
    Args:
        source    : Data source name (postgres/csv/api)
        action    : What was done (query/read/fetch)
        user      : Who accessed the data
        query     : What query was run
        records_returned: How many records came back
        status    : success or error
    """
    # Build log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "action": action,
        "user": user,
        "query": query,
        "records_returned": records_returned,
        "status": status
    }

    # Load existing logs
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    # Append new entry
    logs.append(log_entry)

    # Save back
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print(f" Logged: [{source}] {action} by {user} → {records_returned} records ({status})")


def get_usage_logs(user: str = None, source: str = None) -> list:
    """
    Retrieve usage logs with optional filters.
    """
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            return []

    # Filter by user if provided
    if user:
        logs = [l for l in logs if l["user"] == user]

    # Filter by source if provided
    if source:
        logs = [l for l in logs if l["source"] == source]

    return logs


# ---------- Quick Test ----------
if __name__ == "__main__":
    # Test logging
    log_usage(
        source="postgres",
        action="query",
        user="tejaswee.lashkare",
        query="SELECT * FROM employees",
        records_returned=6
    )
    log_usage(
        source="csv",
        action="read",
        user="bob",
        query="filter department=Analytics",
        records_returned=2
    )
    log_usage(
        source="api",
        action="fetch",
        user="charlie",
        query="GET /market-data",
        records_returned=1
    )

    print("\n--- All Logs ---")
    all_logs = get_usage_logs()
    for log in all_logs:
        print(f"  {log['timestamp']} | {log['source']} | {log['user']}")