import os
from dotenv import load_dotenv
from litellm import completion
load_dotenv()
MODEL = os.getenv("LLM_MODEL")
BUDGET = ("I have GHS 1,200. I want 4 bags of rice at GHS 185 each and "
          "3 gallons of oil at GHS 95 each. How much will I have left?")
FACTS = ["What is the capital of the Bono East Region of Ghana?",
         "<your own factual question here>"]
for q in [BUDGET] * 3 + FACTS:
    r = completion(model=MODEL, temperature=0,
                   messages=[{"role": "user", "content": q}])
    print("Q:", q)
    print("A:", r.choices[0].message.content, "\n" + "-" * 40)