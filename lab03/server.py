"""Lab 3: MCP server for the community pharmacy stock.

Read tools (percepts):  check_stock, search_items, list_expiring, stock_summary
Write tool (actuator):  record_sale  (validated)

Run from inside the lab03/ folder so the data path resolves:
    npx @modelcontextprotocol/inspector python server.py
"""
import csv
import os
from datetime import date, datetime, timedelta

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pharmacy-stock")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "pharmacy_stock.csv")
FIELDS = ["item", "strength", "form", "quantity", "unit_price_ghs", "expiry_date"]


def load() -> list[dict]:
    with open(DATA, newline="") as f:
        return list(csv.DictReader(f))


def save(rows: list[dict]) -> None:
    with open(DATA, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _match(rows: list[dict], item: str, strength: str = "") -> list[dict]:
    rows = [r for r in rows if item.lower().strip() in r["item"].lower()]
    if strength:
        rows = [r for r in rows if strength.lower().strip() in r["strength"].lower()]
    return rows


# ---------------------------------------------------------------- read tools
@mcp.tool()
def check_stock(item: str, strength: str = "") -> list[dict]:
    """Return stock rows whose item name contains item (and strength, if given).

    Use this for questions like "Do we have amoxicillin 500mg?" or "How much
    does paracetamol cost?". Each row has item, strength, form, quantity,
    unit_price_ghs and expiry_date. An empty list means the item is not stocked.
    """
    return _match(load(), item, strength)


@mcp.tool()
def search_items(query: str) -> list[dict]:
    """Search the stock list by free text across item name, strength and form.

    Use this when the user is vague, e.g. "any cough syrups?" or "something
    for malaria". Matches rows where the query appears in the item, strength
    or form. Returns the matching stock rows (may be empty).
    """
    q = query.lower().strip()
    return [r for r in load()
            if q in r["item"].lower() or q in r["strength"].lower() or q in r["form"].lower()]


@mcp.tool()
def list_expiring(days: int = 60) -> list[dict]:
    """List items that expire within the next `days` days (default 60).

    Includes items that have already expired (negative days_left). Results are
    sorted with the earliest expiry first and each row has an extra days_left field.
    """
    if days < 0:
        return [{"error": "days must be zero or positive."}]
    today = date.today()
    limit = today + timedelta(days=days)
    out = []
    for r in load():
        try:
            exp = datetime.strptime(r["expiry_date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if exp <= limit:
            out.append({**r, "days_left": (exp - today).days})
    return sorted(out, key=lambda r: r["days_left"])


@mcp.tool()
def stock_summary() -> dict:
    """Summarise the whole stock: number of product lines, total packs and total value in GHS."""
    rows = load()
    packs = sum(int(r["quantity"]) for r in rows)
    value = sum(int(r["quantity"]) * float(r["unit_price_ghs"]) for r in rows)
    return {"product_lines": len(rows), "total_packs": packs, "total_value_ghs": round(value, 2)}


# --------------------------------------------------------------- write tool
@mcp.tool()
def record_sale(item: str, strength: str, qty: int) -> str:
    """Record a sale and REDUCE the stock quantity. This changes the stock file.

    Call this only when the user clearly asks to sell or record a sale of a
    specific item, strength and number of packs. Do NOT use it to answer
    questions. If several products match, or the stock is not enough, the sale
    is refused and a message explains why: relay that message to the user.
    Returns a confirmation with the new quantity and the total price in GHS.
    """
    if not isinstance(qty, int) or qty <= 0:
        return "REFUSED: qty must be a positive whole number."
    rows = load()
    matches = _match(rows, item, strength)
    if not matches:
        return f"REFUSED: no item matching '{item} {strength}'.".replace("  ", " ")
    if len(matches) > 1:
        names = ", ".join(f"{r['item']} {r['strength']} ({r['form']})" for r in matches)
        return f"REFUSED: more than one product matches ({names}). Ask which one."
    row = matches[0]
    try:
        exp = datetime.strptime(row["expiry_date"], "%Y-%m-%d").date()
        if exp < date.today():
            return f"REFUSED: {row['item']} {row['strength']} expired on {row['expiry_date']}."
    except ValueError:
        pass
    have = int(row["quantity"])
    if qty > have:
        return f"REFUSED: only {have} pack(s) of {row['item']} {row['strength']} in stock, cannot sell {qty}."
    row["quantity"] = str(have - qty)
    save(rows)
    total = round(qty * float(row["unit_price_ghs"]), 2)
    return (f"OK: sold {qty} x {row['item']} {row['strength']} for GHS {total}. "
            f"Remaining stock: {row['quantity']}.")


# ----------------------------------------------- stretch: resource and prompt
@mcp.resource("pharmacy://stock/summary")
def stock_summary_resource() -> str:
    """Read-only stock summary (a resource: data the app can read, not a function the model calls)."""
    s = stock_summary()
    return (f"{s['product_lines']} product lines, {s['total_packs']} packs, "
            f"GHS {s['total_value_ghs']} total value.")


@mcp.prompt()
def stock_check_prompt(item: str) -> str:
    """Reusable prompt template for a stock check."""
    return f"Check whether we have {item} in stock, give the quantity and unit price, and say if it expires within 60 days."


if __name__ == "__main__":
    mcp.run()