
import json
import os
from datetime import datetime

LINEAGE_FILE = "lineage/lineage_store.json"

def record_lineage(
    source_name: str,
    source_type: str,
    query: str,
    fields_accessed: list,
    accessed_by: str,
    transformation: str = "none",
    freshness: str = None
):
    """
    Record full data lineage for every access event.

    Args:
        source_name    : Name of the source (e.g. 'employees_table')
        source_type    : Type of source (postgres/csv/api)
        query          : Query or operation performed
        fields_accessed: List of fields/columns accessed
        accessed_by    : User who accessed the data
        transformation : Any transformation applied
        freshness      : When the data was last updated
    """
    lineage_entry = {
        "lineage_id": f"LIN-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "timestamp": datetime.now().isoformat(),
        "source": {
            "name": source_name,
            "type": source_type,
            "freshness": freshness or datetime.now().isoformat()
        },
        "access": {
            "user": accessed_by,
            "query": query,
            "fields": fields_accessed,
        },
        "transformation": transformation,
        "provenance": f"Data originated from {source_type} source: {source_name}"
    }

    # Load existing lineage records
    records = []
    if os.path.exists(LINEAGE_FILE):
        with open(LINEAGE_FILE, "r") as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

    # Append new entry
    records.append(lineage_entry)

    # Save back
    with open(LINEAGE_FILE, "w") as f:
        json.dump(records, f, indent=2)

    print(f"🔍 Lineage recorded: [{lineage_entry['lineage_id']}] "
          f"{source_name} → accessed by {accessed_by}")
    return lineage_entry["lineage_id"]


def get_lineage(source_name: str = None, user: str = None) -> list:
    """
    Retrieve lineage records with optional filters.
    """
    if not os.path.exists(LINEAGE_FILE):
        return []

    with open(LINEAGE_FILE, "r") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            return []

    if source_name:
        records = [r for r in records if r["source"]["name"] == source_name]

    if user:
        records = [r for r in records if r["access"]["user"] == user]

    return records


def get_data_summary() -> dict:
    """
    Returns a summary of all data sources and their lineage.
    """
    if not os.path.exists(LINEAGE_FILE):
        return {}

    with open(LINEAGE_FILE, "r") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            return {}

    summary = {}
    for r in records:
        src = r["source"]["name"]
        if src not in summary:
            summary[src] = {
                "type": r["source"]["type"],
                "total_accesses": 0,
                "users": set(),
                "fields_accessed": set()
            }
        summary[src]["total_accesses"] += 1
        summary[src]["users"].add(r["access"]["user"])
        summary[src]["fields_accessed"].update(r["access"]["fields"])

    # Convert sets to lists for display
    for src in summary:
        summary[src]["users"] = list(summary[src]["users"])
        summary[src]["fields_accessed"] = list(summary[src]["fields_accessed"])

    return summary


# ---------- Quick Test ----------
if __name__ == "__main__":
    print("=== Recording Lineage ===")

    record_lineage(
        source_name="employees_table",
        source_type="postgres",
        query="SELECT * FROM employees WHERE access_level='admin'",
        fields_accessed=["employee_id", "name", "department", "salary"],
        accessed_by="tejaswee.lashkare",
        transformation="filtered by access_level",
        freshness="2026-06-03T00:00:00"
    )

    record_lineage(
        source_name="sample_data_csv",
        source_type="csv",
        query="filter department=Analytics",
        fields_accessed=["name", "department", "salary"],
        accessed_by="bob",
        transformation="filtered by department"
    )

    record_lineage(
        source_name="market_api",
        source_type="api",
        query="GET /market-data/latest",
        fields_accessed=["price", "volume", "timestamp"],
        accessed_by="charlie",
        transformation="none"
    )

    print("\n=== Lineage Summary ===")
    summary = get_data_summary()
    for source, info in summary.items():
        print(f"\n Source: {source}")
        print(f"   Type       : {info['type']}")
        print(f"   Accesses   : {info['total_accesses']}")
        print(f"   Users      : {info['users']}")
        print(f"   Fields     : {info['fields_accessed']}")