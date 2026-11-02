
import asyncio
import json
import requests
import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

# ─────────────────────────────────────────
# Ollama LLM Call
# ─────────────────────────────────────────
def ask_ollama(context: str, question: str) -> str:
    prompt = f"""You are a helpful data assistant.
Answer the question based ONLY on the data provided below.
Be concise and specific.

Data:
{context}

Question: {question}

Answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


# ─────────────────────────────────────────
# MCP Client — Call Tools
# ─────────────────────────────────────────
async def run_mcp_client():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print(" Connected to MCP Server!\n")

            # List available tools
            tools = await session.list_tools()
            print(" Available MCP Tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")
            print()

            # ── TEST 1: Query PostgreSQL ──
            print("=" * 50)
            print("TEST 1 — Query PostgreSQL (admin only)")
            print("=" * 50)
            result = await session.call_tool(
                "query_postgres",
                {"user": "tejaswee.lashkare", "access_level": "admin"}
            )
            data = json.loads(result.content[0].text)
            context = json.dumps(data["records"], indent=2)
            answer = ask_ollama(context, "Who are the admin level employees and what departments are they in?")
            print(f" Records: {data['count']}")
            print(f" AI Answer: {answer}\n")

            # ── TEST 2: Read CSV ──
            print("=" * 50)
            print("TEST 2 — Read CSV (Analytics department)")
            print("=" * 50)
            result = await session.call_tool(
                "read_csv",
                {"user": "bob", "department": "Analytics"}
            )
            data = json.loads(result.content[0].text)
            context = json.dumps(data["records"], indent=2)
            answer = ask_ollama(context, "What is the average salary in the Analytics department?")
            print(f" Records: {data['count']}")
            print(f" AI Answer: {answer}\n")

            # ── TEST 3: Fetch API ──
            print("=" * 50)
            print("TEST 3 — Fetch Live API Data")
            print("=" * 50)
            result = await session.call_tool(
                "fetch_api",
                {"user": "charlie", "limit": 3}
            )
            data = json.loads(result.content[0].text)
            context = json.dumps(data["records"], indent=2)
            answer = ask_ollama(context, "List the names and their companies from this data.")
            print(f" Records: {data['count']}")
            print(f" AI Answer: {answer}\n")

            # ── TEST 4: Lineage Summary ──
            print("=" * 50)
            print("TEST 4 — Data Lineage Summary")
            print("=" * 50)
            result = await session.call_tool(
                "get_lineage_summary", {}
            )
            data = json.loads(result.content[0].text)
            print(" Lineage Summary:")
            for source, info in data["lineage_summary"].items():
                print(f"   {source}: {info['total_accesses']} accesses by {info['users']}")
            print()

            # ── TEST 5: Usage Logs ──
            print("=" * 50)
            print("TEST 5 — Usage Logs")
            print("=" * 50)
            result = await session.call_tool(
                "get_usage_logs", {}
            )
            data = json.loads(result.content[0].text)
            print(f" Total logs: {data['total']}")
            for log in data["usage_logs"][-3:]:
                print(f"   {log['timestamp']} | {log['source']} | {log['user']}")

            print("\n All MCP Tools tested successfully!")


if __name__ == "__main__":
    asyncio.run(run_mcp_client())