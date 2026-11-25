# Lab 02: Concept Check

> These are draft answers to get you started. Read each one, make sure you
> understand it, then rewrite it in your own words before you submit.

## 1. Thermostat, chess engine, ReAct agent

**Thermostat: reactive.** It has a simple rule ("if the room is too cold, turn
the heating on") and responds straight away to what it senses. It has no memory
and no plan.

**Chess engine: deliberative.** It keeps a model of the board, thinks ahead
through possible moves, and picks the move that best serves its goal of
winning. It plans before it acts.

**ReAct agent: hybrid.** It reacts to every new Observation, which is the
reactive part. But the Thoughts let it plan across several steps, which is the
deliberative part. It has both layers.

## 2. Percepts and actions in the trace

**Percepts** are the things the agent senses from the outside world: the
trader's question, and each **Observation** line (`Observation: 1025` and
`Observation: 175`).

**Actions** are the things the agent does to the world: each
**Action / Action Input** pair (the two calculator calls and the final
`finish` with the answer).

The **Thought** lines are neither. They're the agent's private reasoning
between sensing and acting.

## 3. Why `stop=["Observation:"]`?

A language model just keeps writing the most likely next text. If we didn't stop
it, it would write the tool result itself, and it would make up a number
instead of using the real one. The stop sequence makes it pause right after
the Action Input. Then our code runs the real tool and supplies the real
Observation. That way the model decides *what* to compute, but never *fakes*
the answer.

## 4. The trace as beliefs, desires and intentions

**Belief:** what the agent holds true right now: the budget (GHS 1,200), the
prices, and the results so far (the total cost is 1025). In a ReAct agent,
this is the whole conversation, including every Observation.

**Desire:** the goal the agent wants to achieve: tell the trader how much money
they will have left.

**Intention:** the plan the agent has committed to: first work out the total
cost, then subtract it from the budget, then give the answer. The agent
writes this plan in its Thought lines.