"""
Lab 02, Steps 3 to 5: a ReAct agent built from scratch.

The loop, in plain words:
  1. Ask the model what to do next (it writes Thought, Action, Action Input).
  2. Read the reply with parse().
  3. Run the tool the model asked for.
  4. Show the result back to the model as "Observation: ...".
  5. Repeat until the model says "finish" (or we run out of steps).

Run it:
    python lab02/react_agent.py                      # runs the budget question
    python lab02/react_agent.py "your question here"
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

from tools import calculator, wiki_lookup

load_dotenv()
MODEL = os.getenv("LLM_MODEL")

EVIDENCE = Path(__file__).parent / "evidence"

# The tools the agent is allowed to use. "finish" is handled separately.
TOOLS = {
    "calculator": calculator,
    "wiki_lookup": wiki_lookup,
}

BUDGET_QUESTION = (
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and "
    "3 gallons of oil at GHS 95 each. How much will I have left?"
)

# ---------------------------------------------------------------
# Step 3a: the prompt
# ---------------------------------------------------------------
SYSTEM_PROMPT = """You are a helpful assistant for traders at Makola Market in Accra.

You can use these tools:

calculator   - does arithmetic. Input: an expression like 4*185 + 3*95
wiki_lookup  - gets a short Wikipedia summary. Input: a page title like Techiman
finish       - gives the final answer to the user. Input: the answer itself

On every step, reply in exactly this format and nothing else:

Thought: <your reasoning>
Action: calculator OR wiki_lookup OR finish
Action Input: <input for the tool, or the final answer if the action is finish>

Rules:
- Never do arithmetic in your head. Always use the calculator.
- Never guess facts. Use wiki_lookup.
- Use only one tool per step, then wait for the Observation.
- If you don't need a tool, go straight to finish.
"""

# ---------------------------------------------------------------
# Step 3b: the parser
# ---------------------------------------------------------------
# Finds "Action: something" followed by "Action Input: something".
ACTION_RE = re.compile(r"Action:\s*(\w+)\s*Action Input:\s*(.*)", re.DOTALL)


def parse(text):
    m = ACTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


# ---------------------------------------------------------------
# Talking to the model
# ---------------------------------------------------------------
def ask_model(messages):
    # stop=["Observation:"] means the model must stop before it writes its
    # own Observation. Without it, the model would make up the tool result.
    resp = completion(
        model=MODEL,
        messages=messages,
        temperature=0,
        stop=["Observation:"],
    )
    return resp.choices[0].message.content or ""


# ---------------------------------------------------------------
# Saving the trace
# ---------------------------------------------------------------
def save_trace(lines):
    EVIDENCE.mkdir(exist_ok=True)
    n = len(list(EVIDENCE.glob("trace_*.txt"))) + 1
    path = EVIDENCE / f"trace_{n}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------
# Step 4 + 5: the loop (with error handling)
# ---------------------------------------------------------------
def run_agent(question, max_steps=6):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []

    def log(text):
        print(text)
        trace.append(text)

    log(f"Question: {question}\n")
    answer = None

    for step in range(1, max_steps + 1):
        log(f"--- Step {step} ---")

        # 1. Ask the model (don't crash if the API is down or rate-limited)
        try:
            reply = ask_model(messages)
        except Exception as e:
            log(f"Model error: {e}")
            answer = "Sorry, I could not reach the model."
            break

        log(reply.strip())
        messages.append({"role": "assistant", "content": reply})

        # 2. Read the reply
        action, action_input = parse(reply)

        # 3. Decide what to do
        if action is None:
            # Failure 1: we couldn't read the reply
            observation = ("I could not read your reply. Please use exactly this format: "
                           "Thought: ... then Action: ... then Action Input: ...")
        elif action == "finish":
            answer = action_input
            break
        elif action not in TOOLS:
            # Failure 2: the model asked for a tool that doesn't exist
            observation = (f"There is no tool called '{action}'. "
                           "Choose calculator, wiki_lookup or finish.")
        else:
            # Run the real tool, using only the first line of the input
            first_line = action_input.split("\n")[0]
            observation = TOOLS[action](first_line)

        # 4. Give the result back to the model
        log(f"Observation: {observation}\n")
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    # Failure 3: we hit max_steps without a finish
    if answer is None:
        answer = f"I could not finish within {max_steps} steps."

    log(f"\nFinal answer: {answer}")

    path = save_trace(trace)
    print(f"(trace saved to {path})")
    return answer


# ---------------------------------------------------------------
if __name__ == "__main__":
    if not MODEL:
        print("LLM_MODEL is not set. Copy .env.example to .env and check it.")
        sys.exit(1)

    question = " ".join(sys.argv[1:]) or BUDGET_QUESTION
    run_agent(question)