# Baseline: the model on its own (no tools)

Model: groq/openai/gpt-oss-20b
Date: 2026-11-25

## Budget question

> I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?

The right answer is GHS 175.

### Run 1

Let’s calculate the total cost first:

- **Rice:** 4 bags × GHS 185 = GHS 740  
- **Oil:** 3 gallons × GHS 95 = GHS 285  

**Total spent:**  
GHS 740 + GHS 285 = GHS 1,025  

You started with GHS 1,200, so the remaining amount is:

GHS 1,200 − GHS 1,025 = GHS 175

**You will have GHS 175 left.**

**Correct?** (write yes or no)

### Run 2

Total cost:
- 4 bags of rice: 4 × GHS 185 = **GHS 740**
- 3 gallons of oil: 3 × GHS 95  = **GHS 285**

**Total spent** = 740 + 285 = **GHS 1,025**

With an initial GHS 1,200:

**Remaining amount** = 1,200 – 1,025 = **GHS 175**.

**Correct?** (write yes or no)

### Run 3

You’ll spend:

- **Rice:** 4 × 185 GHS = **740 GHS**  
- **Oil:** 3 × 95 GHS = **285 GHS**

Total spent: 740 GHS + 285 GHS = **1 025 GHS**

Starting with 1 200 GHS, you’ll have:

1 200 GHS – 1 025 GHS = **175 GHS** left.

**Correct?** (write yes or no)

## Factual questions

### What is the capital of the Bono East Region of Ghana?

The capital of the Bono East Region of Ghana is **Techiman**.

**Correct?** (write yes or no)
**Did it sound confident?** (write a few words)

### How many stalls are there in Makola Market in Accra?

Makola Market is the largest and most bustling market in Accra, and its size is often described in terms of the sheer number of individual stalls that line its lanes.  Estimates from journalists, market‑workers and the Ghana Tourism Authority put the count at roughly **5 000 to 10 000 stalls** – a wide range that reflects the market’s fluid nature (stalls can be set up or removed day‑to‑day).  In practice, the market usually operates at about **8 000 stalls** at any given time, making it one of the busiest marketplaces in West Africa.  (Numbers can vary with seasonal activity and administrative changes, but 8 000 is the figure most commonly cited by local authorities.)

**Correct?** (write yes or no)
**Did it sound confident?** (write a few words)
