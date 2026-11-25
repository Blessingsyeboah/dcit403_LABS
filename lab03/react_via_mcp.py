"""Lab 3, Wednesday: the Lab 2 ReAct agent, with tools discovered from the MCP server.

Still the text protocol (Thought / Action / Action Input / Observation), but the
tool list in the prompt is built from session.list_tools() and tools run through
session.call_tool(). Action Input for MCP tools is a JSON object.

Run from inside lab03/:
    python react_via_mcp.py "Do we have amoxicillin 500mg, and what would 3 packs cost?"
The trace is saved to evidence/react_via_mcp.txt.
"""
import asyncio
import json
import os
import re
import sys

from dotenv import load_dotenv
from litellm import acompletion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
TRACE_PATH = os.path.join("evidence", "react_via_mcp.txt")

params = StdioServerParameters(command=sys.executable, args=["server.py"])

# Lab 2 parser, but the action name may now be followed by anything on its line.
ACTION_RE = re.compile(r"Action:\s*(\w+)\s*\n\s*Action Input:\s*(.*)", re.DOTALL)


def parse(text: str):
    m = ACTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def build_prompt(tools) -> str:
    lines = []
    for t in tools:
        props = t.inputSchema.get("properties", {})
        required = set(t.inputSchema.get("required", []))
        args = ", ".join(f"{k}: {v.get('type', 'any')}{'' if k in required else ' (optional)'}"
                         for k, v in props.items())
        desc = " ".join((t.description or "").split())
        lines.append(f"- {t.name}({args}): {desc}")
    tool_block = "\n".join(lines)
    return f"""You are a pharmacy stock assistant that solves problems step by step.

Tools:
{tool_block}
- finish(answer): give the final answer to the user.

On EVERY step reply in exactly this format:
Thought: <your reasoning>
Action: <one tool name from the list above, or finish>
Action Input: <a JSON object with the tool's arguments, e.g. {{"item": "amoxicillin"}}; for finish just the answer text>

Rules: use one action per reply. Never write an Observation yourself. Never invent stock
or prices. Only call record_sale if the user explicitly asks to record a sale."""


def parse_args(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```\w*\s*|\s*```$", "", raw).strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


async def run_agent(session: ClientSession, tools, question: str, max_steps: int = 6) -> str:
    tool_names = {t.name for t in tools}
    messages = [{"role": "system", "content": build_prompt(tools)},
                {"role": "user", "content": question}]
    trace = [f"Question: {question}"]

    def emit(line: str):
        print(line)
        trace.append(line)

    final = "Stopped: reached max_steps without a final answer."
    for _ in range(max_steps):
        resp = await acompletion(model=MODEL, messages=messages, temperature=0,
                                 stop=["Observation:"])
        reply = resp.choices[0].message.content or ""
        emit(reply.strip())
        messages.append({"role": "assistant", "content": reply})

        action, action_input = parse(reply)
        if action is None:
            obs = ("Could not parse your reply. Use exactly:\nThought: ...\n"
                   "Action: <tool name or finish>\nAction Input: <JSON object, or the answer for finish>")
        elif action == "finish":
            final = action_input
            break
        elif action not in tool_names:
            obs = f"Unknown action '{action}'. Choose one of: {', '.join(sorted(tool_names))}, finish."
        else:
            args = parse_args(action_input)
            if args is None:
                obs = "Action Input must be a valid JSON object, e.g. {\"item\": \"amoxicillin\"}."
            else:
                try:
                    result = await session.call_tool(action, args)
                    obs = "\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")
                    if result.isError:
                        obs = f"Tool error: {obs}"
                except Exception as e:
                    obs = f"Tool error: {e}"
        emit(f"Observation: {obs}")
        messages.append({"role": "user", "content": f"Observation: {obs}"})

    emit(f"Final answer: {final}")
    os.makedirs("evidence", exist_ok=True)
    with open(TRACE_PATH, "a") as f:
        f.write("\n".join(trace) + "\n\n" + "=" * 60 + "\n\n")
    return final


async def main() -> None:
    if not MODEL:
        raise SystemExit("LLM_MODEL is not set. Check your .env file.")
    question = " ".join(sys.argv[1:]) or "Do we have amoxicillin 500mg, and what would 3 packs cost?"
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print("Discovered tools:", ", ".join(t.name for t in tools), "\n")
            await run_agent(session, tools, question)


if __name__ == "__main__":
    asyncio.run(main())