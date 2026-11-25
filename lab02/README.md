# Lab 02: A ReAct Agent From Scratch

Hi! This is the Makola Market helper. A trader asks something like
*"I have GHS 1,200 and want 4 bags of rice at GHS 185 each and 3 gallons of
oil at GHS 95 each. How much will I have left?"* and the agent works it out.

The big idea of this lab is simple: **the model never does the maths and never
looks anything up. It only decides what to do next.** Our Python code does the
actual work and tells the model what happened.

## What's in this folder

| File | What it does | Lab step |
| --- | --- | --- |
| `baseline.py` | Asks the model the questions with no tools, so you can see where it goes wrong | Step 1 |
| `tools.py` | The calculator and the Wikipedia lookup | Step 2 |
| `react_agent.py` | The prompt, the parser and the loop. This is the heart of the lab | Steps 3 to 5 |
| `run_tests.py` | Runs six questions in one go and saves a trace for each | Step 5 |
| `concept_check.md` | Draft answers to the concept check (rewrite them in your own words) | Part A |
| `evidence/` | Where your baseline and traces end up | |

## Before you start

You need your Codespace open, your keys set up and `.env` created, same as
Lab 1. If `echo $GROQ_API_KEY | cut -c1-6` shows six characters, you're good.

Drop this whole `lab02` folder into the root of your lab repository, next to `lab01`.

## Running it, step by step

Run everything from the **root of your repository**, not from inside `lab02`.

**Step 1: baseline**

```bash
python lab02/baseline.py
```

Open `lab02/evidence/baseline.md` and fill in each "Correct?" line yourself.
The right budget answer is GHS 175. For the two factual questions, look the
answers up and notice how sure the model sounds even when it's wrong. (The
Makola stall question is a trick: nobody really knows the exact number.)

**Step 2: test the tools**

```bash
python lab02/tools.py
```

You should see 1025, 175, -3, and then an error for the `__import__('os')`
line. That error is the point. It proves the calculator rejects sneaky input.

**Step 3 and 4: run the agent**

```bash
python lab02/react_agent.py
```

With no question, it runs the budget question. You should see two calculator
calls and then a finish, a lot like the trace you did by hand in Part A. You
can also ask your own question:

```bash
python lab02/react_agent.py "What is the capital of the Bono East Region?"
```

Every run prints its trace and saves it as `evidence/trace_1.txt`,
`trace_2.txt` and so on.

**Step 5: break it**

```bash
python lab02/run_tests.py
```

This runs the budget question plus five others (two that need both tools, a
Wikipedia page that doesn't exist, one that needs no tool, and one badly
worded). That gives you your six traces. Then commit and push:

```bash
git add lab02
git commit -m "lab02: react agent"
git push
```

Use a separate commit for each step if you can. The manual asks for that.

## How the agent works (in plain English)

Each time round the loop, the model writes three lines:

```
Thought: I need the total cost first.
Action: calculator
Action Input: 4*185 + 3*95
```

Our code reads those lines (`parse`), runs the tool, and sends back:

```
Observation: 1025
```

Then the model thinks again. It keeps going until it picks the action `finish`.

Two small details matter a lot:

- **`stop=["Observation:"]`**: this tells the model to stop writing before it
  gets to the Observation line. Otherwise it would happily invent a tool result.
- **`max_steps`**: a confused agent can loop forever and burn through your free
  requests. The step limit is the safety net.

## What happens when things go wrong

The loop never crashes on these. It either tells the model what went wrong or
stops politely.

| Problem | What the agent does |
| --- | --- |
| The reply isn't in the Thought/Action format | Sends back an Observation that explains the format, so the model can try again |
| The model asks for a tool that doesn't exist | Sends back an Observation listing the real tools |
| The model keeps going and never finishes | Stops at `max_steps` and says so |
| The API fails or you hit a rate limit | Logs the error and stops instead of crashing |

## If something goes wrong on your side

- **`LLM_MODEL is not set`**: copy `.env.example` to `.env` and check the model name.
- **A 429 error**: you've hit the free-tier limit. Wait a minute, or switch
  `LLM_MODEL` to the Gemini backup in `.env`.
- **`ModuleNotFoundError: tools`**: run the command from the repo root exactly
  as written above (`python lab02/react_agent.py`).
- **Wikipedia says "Could not reach"**: check your internet connection in the Codespace and try again.

## Before you submit

Reading the code is not enough. You need to be able to explain every line.

- [ ] Fill in the "Correct?" lines in `evidence/baseline.md`
- [ ] Rewrite `concept_check.md` in your own words
- [ ] Check you have at least six traces in `evidence/`
- [ ] Pick one failure trace for your report (your own, from a real run)
- [ ] Add your AI-use log entry (see below)
- [ ] Check that no `.env` file got committed

### AI-use log

If an AI tool helped you with this lab, it goes in `AI_USE_LOG.md`. Here's an
example row you can adapt to what you actually did:

| Date | Lab | Tool | What I asked | What I used | What I changed or checked |
| --- | --- | --- | --- | --- | --- |
| 25 Nov | Lab 2 | Claude | Build the Lab 02 code files and docs from the manual | The starter code for tools.py and react_agent.py | Ran every step myself, read each line, rewrote the concept check in my own words |

Edit the date and details so they're true for you.

## Report hints

The report asks three things. Here's where to look:

- **Deliberative vs reactive parts of the loop:** the Thought is the model
  planning ahead. Reacting to each Observation, and the error handling, is
  reactive behaviour.
- **Baseline vs ReAct on the budget question:** compare your three baseline
  answers with your agent's trace. How many were right in each case?
- **One failure trace:** use a real one from your own runs. Say what went
  wrong, why, and what you changed.

## Stretch ideas (optional)

- Add a `convert_currency(amount, from_cur, to_cur)` tool with a small table of rates you make up.
- Print the total tokens used at the end of each run (`resp.usage.total_tokens`).
- Add a reactive shortcut: if the question is only numbers and operators, call the calculator without asking the model.