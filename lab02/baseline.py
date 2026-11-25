"""
Lab 02, Step 1: the baseline. The model on its own, with no tools.

This asks the budget question three times and two factual questions,
then writes the answers to lab02/evidence/baseline.md.

Run it:
    python lab02/baseline.py

Then open baseline.md and fill in the "Correct?" lines yourself.
Checking the answers is your job, not the script's.
"""

import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")

EVIDENCE = Path(__file__).parent / "evidence"

BUDGET_QUESTION = (
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and "
    "3 gallons of oil at GHS 95 each. How much will I have left?"
)

FACT_QUESTIONS = [
    "What is the capital of the Bono East Region of Ghana?",
    "How many stalls are there in Makola Market in Accra?",
]


def ask(question):
    # temperature=1 so you can see how the answers wobble from run to run
    resp = completion(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        temperature=1,
    )
    return resp.choices[0].message.content or ""


if __name__ == "__main__":
    if not MODEL:
        print("LLM_MODEL is not set. Copy .env.example to .env and check it.")
        sys.exit(1)

    EVIDENCE.mkdir(exist_ok=True)
    lines = [
        "# Baseline: the model on its own (no tools)",
        "",
        f"Model: {MODEL}",
        f"Date: {date.today()}",
        "",
        "## Budget question",
        "",
        f"> {BUDGET_QUESTION}",
        "",
        "The right answer is GHS 175.",
        "",
    ]

    for i in range(1, 4):
        print(f"Budget question, run {i} of 3...")
        lines += [f"### Run {i}", "", ask(BUDGET_QUESTION), "",
                  "**Correct?** (write yes or no)", ""]

    lines += ["## Factual questions", ""]
    for q in FACT_QUESTIONS:
        print(f"Asking: {q}")
        lines += [f"### {q}", "", ask(q), "",
                  "**Correct?** (write yes or no)",
                  "**Did it sound confident?** (write a few words)", ""]

    path = EVIDENCE / "baseline.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDone. Open {path} and mark each answer.")