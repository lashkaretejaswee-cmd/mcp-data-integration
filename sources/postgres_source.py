
import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.usage_logger import log_usage
from lineage.tracker import record_lineage

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="mcp_integration",
        user="prathamesh.pawar",
        password=""
    )

def query_employees(user: str, access_level: str = None) -> list:
    """
    Query employees table with optional access level filter.
    Logs usage and records lineage on every call.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if access_level:
        cursor.execute(
            "SELECT * FROM employees WHERE access_level = %s",
            (access_level,)
        )
        query_str = f"SELECT * FROM employees WHERE access_level='{access_level}'"
    else:
        cursor.execute("SELECT * FROM employees")
        query_str = "SELECT * FROM employees"

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    # Format as list of dicts
    results = [dict(zip(columns, row)) for row in rows]

    # Log usage
    log_usage(
        source="postgres",
        action="query",
        user=user,
        query=query_str,
        records_returned=len(results)
    )

    # Record lineage
    record_lineage(
        source_name="employees_table",
        source_type="postgres",
        query=query_str,
        fields_accessed=columns,
        accessed_by=user,
        transformation=f"filtered by access_level={access_level}" if access_level else "none"
    )

    return results


# ---------- Quick Test ----------
if __name__ == "__main__":
    print("=== PostgreSQL Source Test ===")
    results = query_employees("tejaswee.lashkare")
    print(f"Total records: {len(results)}")
    for r in results:
        print(f"  {r['employee_id']} | {r['name']} | {r['department']} | {r['access_level']}")