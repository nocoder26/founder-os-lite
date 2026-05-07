---
name: interview
description: Generate a discipline-driven customer interview script from the current problem hypothesis. After the interview, extract atomic signals (verbatim quotes, observed behaviors) into the brain.
---

# /interview

Read `brain/problem.md`. If empty, refuse — *"No problem hypothesis yet. Run `/problem` first."*

## Two modes: PRE and POST

Ask the founder which: *"Are we (a) prepping for an upcoming interview, or (b) extracting signals from one you just did?"*

## PRE mode — generate the script

Produce an interview-discipline script tailored to the current problem hypothesis. The script focuses on **past behavior, not opinions about the future.**

### Interview-discipline rules embedded in every script:

1. Talk about their life, not your idea
2. Ask about specifics in the past, not generics or opinions about the future
3. Talk less, listen more

### Required sections of every script:

```
## Opening (2 min)
- Who they are, what they do
- Set expectation: "I'm researching, not selling. Just want to learn."

## Problem discovery (15 min) — past behavior only
- "Walk me through the last time [problem context happened]."
- "What did you do when that happened?"
- "How often does that come up?"
- "What's the worst part of that for you?"
- "What have you tried to fix it?"
- "How much does it cost you — in time or money?"

## Believer test (5 min) — earlyvangelist signals
- "Have you ever paid for anything to solve this?"
- "What would 'solved' look like for you?"
- "Who else has this problem?"

## Close (3 min)
- "Anything else I should be asking?"
- "Can I follow up in [N] weeks?"
- "Can you connect me with one other person who has this?"
```

Add 2-3 questions specific to THIS founder's hypothesis (e.g., if hypothesis is about late invoices, add: *"Walk me through the last invoice you had to chase. What did that day look like?"*).

**Anti-questions** (warn the founder NOT to ask these):
- "Would you pay for a product that does X?" (opinion about future, useless)
- "Do you think this is a problem?" (compliments, useless)
- "Would you use [your solution]?" (sells, doesn't learn)

## POST mode — extract signals

Founder pastes interview notes or transcript. Extract these atomic signals only:

**Verbatim quotes** — exact words about the pain, current alternatives, or willingness to pay.  
**Observed behaviors** — what they DO, not what they SAY (already paid for X, tried Y three times, runs a workflow on Sundays).  
**Money already spent** — on workarounds, adjacent tools, manual labor.  
**Frequency mentions** — every Friday, every quarter, twice a week.

### Earlyvangelist test (Blank) — score the participant

Five criteria. Yes/No each:
- Has the problem
- Knows it's a problem (named it specifically, not led)
- Has tried to solve it (workarounds, other tools, hiring)
- Has budget (already spends on adjacent tools)
- Would pay for the solution (in their own words, not led)

**5/5 = BELIEVER**. **3-4 = NEUTRAL**. **0-2 = INFIDEL**.

### Write to `brain/interviews/N-<short-name>.md`

```markdown
---
date: <today>
participant: <name, role, company, segment>
recruited_via: <how you found them>
classification: BELIEVER | NEUTRAL | INFIDEL
---

## Pain admitted (verbatim quotes only)
> "..."
> "..."

## Behavior observed
- ...
- ...

## Earlyvangelist test (Blank)
- Has the problem: yes/no
- Knows it's a problem: yes/no
- Has tried to solve it: yes/no
- Has budget: yes/no
- Would pay: yes/no
→ Classification: BELIEVER / NEUTRAL / INFIDEL

## Hypothesis impact
- Confirms: ...
- Contradicts: ...
- Action: ...
```

### Update related files

- Append the participant to `brain/believers/index.md` (create if missing) with their classification and one-line summary
- If the interview contradicts `brain/problem.md`, suggest `/problem` to refine

### Re-evaluate the hypothesis

After every 3 interviews, surface patterns:  
*"3 of 5 mentioned X — your script doesn't ask about it. Add?"*  
*"60% of believers are in segment Y. You might have a niche, not a market. Lean in or expand?"*

## Stage gate check

If `brain/believers/` now contains 5+ entries marked `BELIEVER`, suggest advancing `brain/stage.md` from `1` to `2`. Don't auto-advance — surface the option:  
*"5 believers identified. Stage 1 → 2 gate met. `product/` writes will become allowed (still coached against evidence). Advance?"*
