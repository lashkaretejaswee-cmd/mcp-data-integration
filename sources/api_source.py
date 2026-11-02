
import urllib.request
import urllib.error
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.usage_logger import log_usage
from lineage.tracker import record_lineage

# Using free public API - no key needed
API_URL = "https://jsonplaceholder.typicode.com/users"

def fetch_api_data(user: str, limit: int = 3) -> list:
    """
    Fetch data from a public REST API.
    Logs usage and records lineage on every call.
    """
    try:
        request = urllib.request.Request(
            API_URL,
            headers={"User-Agent": "MCP-Integration/1.0"}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            raw_data = json.loads(response.read().decode())

        # Take only 'limit' records and extract key fields
        results = []
        for item in raw_data[:limit]:
            results.append({
                "id": item["id"],
                "name": item["name"],
                "email": item["email"],
                "company": item["company"]["name"],
                "city": item["address"]["city"]
            })

        query_str = f"GET {API_URL} limit={limit}"

        # Log usage
        log_usage(
            source="api",
            action="fetch",
            user=user,
            query=query_str,
            records_returned=len(results)
        )

        # Record lineage
        record_lineage(
            source_name="market_api",
            source_type="api",
            query=query_str,
            fields_accessed=["id", "name", "email", "company", "city"],
            accessed_by=user,
            transformation=f"limited to {limit} records"
        )

        return results

    except urllib.error.URLError as e:
        log_usage(
            source="api",
            action="fetch",
            user=user,
            query=API_URL,
            records_returned=0,
            status="error"
        )
        print(f"API Error: {e}")
        return []


# ---------- Quick Test ----------
if __name__ == "__main__":
    print("=== API Source Test ===\n")

    results = fetch_api_data("tejaswee.lashkare", limit=3)
    print(f"Total records fetched: {len(results)}")
    for r in results:
        print(f"  {r['id']} | {r['name']} | {r['company']} | {r['city']}")