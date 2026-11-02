
import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.usage_logger import log_usage
from lineage.tracker import record_lineage

CSV_FILE = "data/sample_data.csv"

def read_csv(user: str, department: str = None) -> list:
    """
    Read CSV file with optional department filter.
    Logs usage and records lineage on every call.
    """
    results = []

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("employee_id"):
                continue  # Skip rows without employee_id
            if department:
                if row["department"] == department:
                    results.append(row)
            else:
                results.append(row)

    query_str = f"read CSV filter department={department}" if department else "read all CSV"
    fields = ["employee_id", "name", "department", "salary", "access_level"]

    # Log usage
    log_usage(
        source="csv",
        action="read",
        user=user,
        query=query_str,
        records_returned=len(results)
    )

    # Record lineage
    record_lineage(
        source_name="sample_data_csv",
        source_type="csv",
        query=query_str,
        fields_accessed=fields,
        accessed_by=user,
        transformation=f"filtered by department={department}" if department else "none"
    )

    return results


# ---------- Quick Test ----------
if __name__ == "__main__":
    print("=== CSV Source Test ===\n")

    print("-- All records --")
    all_data = read_csv("tejaswee.lashkare")
    print(f"Total records: {len(all_data)}")
    for r in all_data:
        print(f"  {r['employee_id']} | {r['name']} | {r['department']}")

    print("\n-- Filtered: Analytics only --")
    analytics = read_csv("bob", department="Analytics")
    print(f"Total records: {len(analytics)}")
    for r in analytics:
        print(f"  {r['employee_id']} | {r['name']} | {r['department']}")