"""
Lab 02, Step 5: run the budget question plus five more.

Each run saves its own trace in lab02/evidence/, so after this
you will have six traces (the Deliverables ask for at least six).

Run it:
    python lab02/run_tests.py
"""

import os
import sys
import time

from react_agent import run_agent, BUDGET_QUESTION

QUESTIONS = [
    # The budget question (Step 4)
    BUDGET_QUESTION,

    # Needs both tools
    "What is the capital of the Bono East Region, and how much would 12 bags "
    "of maize at GHS 240 each cost in total?",

    # Needs both tools
    "Find out what Cape Coast is known for, then work out the cost of "
    "7 boxes of fish at GHS 130 each.",

    # Wikipedia page that does not exist
    "Tell me about the Wikipedia page for the Zorblax Market Union.",

    # Needs no tool
    "Say hello to a trader in one friendly sentence.",

    # Deliberately badly worded
    "rice cost many how 4 bag 185 and 1200 left??",
]

if __name__ == "__main__":
    if not os.getenv("LLM_MODEL"):
        # react_agent has already loaded .env by this point
        print("LLM_MODEL is not set. Copy .env.example to .env and check it.")
        sys.exit(1)

    for q in QUESTIONS:
        run_agent(q)
        print("\n" + "=" * 60 + "\n")
        time.sleep(2)  # small pause, kind to the free-tier rate limit