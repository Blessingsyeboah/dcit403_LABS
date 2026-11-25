"""Lab 3, Steps 3 to 5: an agent that discovers its tools from the MCP server.

The agent never imports the tool functions. It starts server.py over stdio,
lists the tools, sends their schemas to the model, runs the tool calls through
the MCP session and logs every call to evidence/tool_calls.jsonl.

Run from inside lab03/:
    python client_agent.py                 # interactive
    python client_agent.py --demo          # runs the six demo questions
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from litellm import acompletion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
MAX_STEPS = 6
LOG_PATH = os.path.join("evidence", "tool_calls.jsonl")

SYSTEM = (
    "You are an assistant for a community pharmacy. Answer stock, price and expiry "
    "questions using the tools; never guess quantities or prices. Use record_sale "
    "only when the user clearly asks to record a sale. If a tool refuses, explain "
    "the reason to the user. Never oversell. Keep answers short. "
    "All prices are in Ghana cedis (GHS)."
)

DEMO_QUESTIONS = [
    "Do we have amoxicillin 500mg?",
    "Which items expire within 60 days?",
    "What do 2 packs of paracetamol cost?",
    "Sell 2 packs of paracetamol 500mg.",
    "Sell 9999 packs of paracetamol 500mg.",
    "Any cough syrups in stock?",
]

params = StdioServerParameters(command=sys.executable, args=["server.py"])


def log_call(name: str, args: dict, result_text: str, ms: float) -> None:
    os.makedirs("evidence", exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": name,
        "arguments": args,
        "result_summary": (result_text[:200] + "...") if len(result_text) > 200 else result_text,
        "duration_ms": round(ms, 1),
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def result_to_text(result) -> str:
    parts = [c.text for c in result.content if getattr(c, "type", "") == "text"]
    return "\n".join(parts) if parts else str(result.content)


async def run_agent(session: ClientSession, schemas: list[dict], question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(MAX_STEPS):
        resp = await acompletion(model=MODEL, messages=messages, tools=schemas, temperature=0)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg.model_dump())
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            start = time.perf_counter()
            try:
                result = await session.call_tool(name, args)
                text = result_to_text(result)
                if result.isError:
                    text = f"Tool error: {text}"
            except Exception as e:
                text = f"Tool error: {e}"
            ms = (time.perf_counter() - start) * 1000
            log_call(name, args, text, ms)
            print(f"  [tool] {name}({args}) -> {text[:120]}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})
    return "Stopped: reached the maximum number of steps."


async def main() -> None:
    if not MODEL:
        raise SystemExit("LLM_MODEL is not set. Check your .env file.")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print("Discovered tools:", ", ".join(t.name for t in tools))
            schemas = [{"type": "function", "function": {
                "name": t.name, "description": t.description,
                "parameters": t.inputSchema}} for t in tools]

            if "--demo" in sys.argv:
                for q in DEMO_QUESTIONS:
                    print(f"\nQ: {q}")
                    print("A:", await run_agent(session, schemas, q))
                    await asyncio.sleep(2)  # be gentle with free-tier rate limits
                return

            print("Type a question, or 'quit' to exit.")
            while True:
                q = input("\nYou: ").strip()
                if q.lower() in {"quit", "exit"}:
                    break
                if q:
                    print("Bot:", await run_agent(session, schemas, q))


if __name__ == "__main__":
    asyncio.run(main())