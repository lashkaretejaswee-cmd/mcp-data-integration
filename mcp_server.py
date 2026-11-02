
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from sources.postgres_source import query_employees
from sources.csv_source import read_csv
from sources.api_source import fetch_api_data
from lineage.tracker import get_lineage, get_data_summary
from logs.usage_logger import get_usage_logs

# Initialize MCP Server
server = Server("mcp-data-integration")

# ─────────────────────────────────────────
# TOOL 1 — Query PostgreSQL Employees
# ─────────────────────────────────────────
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_postgres",
            description="Query employee data from PostgreSQL database with optional access level filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "Username making the request"
                    },
                    "access_level": {
                        "type": "string",
                        "description": "Filter by access level: admin, analyst, intern (optional)",
                        "enum": ["admin", "analyst", "intern"]
                    }
                },
                "required": ["user"]
            }
        ),
        types.Tool(
            name="read_csv",
            description="Read employee data from CSV file with optional department filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "Username making the request"
                    },
                    "department": {
                        "type": "string",
                        "description": "Filter by department: Engineering, Analytics, Operations (optional)"
                    }
                },
                "required": ["user"]
            }
        ),
        types.Tool(
            name="fetch_api",
            description="Fetch live data from external REST API",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "Username making the request"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of records to fetch (default: 3)"
                    }
                },
                "required": ["user"]
            }
        ),
        types.Tool(
            name="get_lineage_summary",
            description="Get data lineage and usage summary for all sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "Filter lineage by user (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_usage_logs",
            description="Get usage logs showing who accessed what data and when",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "string",
                        "description": "Filter logs by user (optional)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Filter logs by source: postgres, csv, api (optional)"
                    }
                }
            }
        )
    ]


# ─────────────────────────────────────────
# TOOL HANDLER — Execute Tools
# ─────────────────────────────────────────
@server.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:

    if name == "query_postgres":
        user = arguments.get("user", "anonymous")
        access_level = arguments.get("access_level")
        results = query_employees(user=user, access_level=access_level)
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "source": "PostgreSQL",
                "user": user,
                "records": results,
                "count": len(results)
            }, indent=2, default=str)
        )]

    elif name == "read_csv":
        user = arguments.get("user", "anonymous")
        department = arguments.get("department")
        results = read_csv(user=user, department=department)
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "source": "CSV",
                "user": user,
                "records": results,
                "count": len(results)
            }, indent=2)
        )]

    elif name == "fetch_api":
        user = arguments.get("user", "anonymous")
        limit = arguments.get("limit", 3)
        results = fetch_api_data(user=user, limit=limit)
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "source": "REST API",
                "user": user,
                "records": results,
                "count": len(results)
            }, indent=2)
        )]

    elif name == "get_lineage_summary":
        user = arguments.get("user")
        summary = get_data_summary()
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "lineage_summary": summary
            }, indent=2)
        )]

    elif name == "get_usage_logs":
        user = arguments.get("user")
        source = arguments.get("source")
        logs = get_usage_logs(user=user, source=source)
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "usage_logs": logs,
                "total": len(logs)
            }, indent=2)
        )]

    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


# ─────────────────────────────────────────
# RUN SERVER
# ─────────────────────────────────────────
async def main():
    print("🚀 MCP Data Integration Server starting...", file=sys.stderr)
    print("📡 Tools available: query_postgres, read_csv, fetch_api, get_lineage_summary, get_usage_logs", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())