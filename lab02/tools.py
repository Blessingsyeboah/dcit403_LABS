"""
Lab 02, Step 2: the tools.

The model never does the work itself. It only asks for a tool by name,
and our code runs it. There are two tools here:

  calculator   - safe arithmetic (no eval, ever)
  wiki_lookup  - a short summary from Wikipedia

Run this file on its own to test both tools before using them in the agent:
    python lab02/tools.py
"""

import ast
import operator as op

import requests

# ---------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------
# We only allow these operations. Anything else gets rejected.
OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
}


def _eval(node):
    # A plain number
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    # Something like 4 * 185
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    # Something like -5
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    # Anything else (function calls, names, imports...) is not allowed
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        expr = expression.replace(",", "")  # so "1,200" works
        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------
# Wikipedia lookup
# ---------------------------------------------------------------
def wiki_lookup(title: str) -> str:
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + title.strip().replace(" ", "_"))
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"})
    except Exception as e:
        return f"Could not reach Wikipedia: {e}"
    if r.status_code != 200:
        return f"No Wikipedia page found for '{title}'."
    return r.json().get("extract", "")[:800]


# ---------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("calculator('4*185 + 3*95')      ->", calculator("4*185 + 3*95"))
    print("calculator('1,200 - 1025')      ->", calculator("1,200 - 1025"))
    print("calculator('-5 + 2')            ->", calculator("-5 + 2"))
    print("calculator(\"__import__('os')\")  ->", calculator("__import__('os')"))
    print()
    print("wiki_lookup('Techiman') ->")
    print(wiki_lookup("Techiman"))
    print()
    print("wiki_lookup('Zorblax Market Union') ->")
    print(wiki_lookup("Zorblax Market Union"))