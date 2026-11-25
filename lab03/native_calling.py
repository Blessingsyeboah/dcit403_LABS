"""Lab 3, Step 1: native function calling (no MCP yet).

Run from inside the lab03/ folder:  python native_calling.py
"""
import csv
import json
import os

from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
DATA = "data/pharmacy_stock.csv"


def check_stock(item: str, strength: str = "") -> list[dict]:
    """Return stock rows whose item name contains item (and strength, if given)."""
    with open(DATA, newline="") as f:
        rows = [r for r in csv.DictReader(f) if item.lower() in r["item"].lower()]
    if strength:
        rows = [r for r in rows if strength.lower() in r["strength"].lower()]
    return rows


TOOLS = {"check_stock": check_stock}

tool_schemas = [{
    "type": "function",
    "function": {
        "name": "check_stock",
        "description": (
            "Look up pharmacy stock. Returns rows with item, strength, form, "
            "quantity, unit_price_ghs and expiry_date. Use for any question about "
            "whether an item is available, how many are left, or its price."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Drug name, e.g. 'amoxicillin'."},
                "strength": {"type": "string", "description": "Optional strength, e.g. '500mg'."},
            },
            "required": ["item"],
        },
    },
}]


def ask(question: str) -> str:
    messages = [
        {"role": "system", "content": "You are a pharmacy stock assistant. Use tools for stock facts; never guess."},
        {"role": "user", "content": question},
    ]
    for _ in range(5):  # step limit
        resp = completion(model=MODEL, messages=messages, tools=tool_schemas, temperature=0)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg.model_dump())
        for tc in msg.tool_calls:
            print(f"[tool call] {tc.function.name}({tc.function.arguments})")
            try:
                args = json.loads(tc.function.arguments)
                result = TOOLS[tc.function.name](**args)
            except Exception as e:  # unknown tool, bad args, etc.
                result = f"Error: {e}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return "Stopped: too many steps."


if __name__ == "__main__":
    if not MODEL:
        raise SystemExit("LLM_MODEL is not set. Check your .env file.")
    print(ask("Do we have amoxicillin 500mg?"))