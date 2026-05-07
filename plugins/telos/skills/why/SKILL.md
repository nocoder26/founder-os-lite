---
name: why
description: Capture or recall the founder's motivation. Two modes — initial capture (5 questions), or recall mode when the founder is about to quit, pivot, or stop doing the work. Surfaces their own past words back at them.
---

# /why

Read `brain/why.md` (may be empty). Read `brain/journey.md` if it exists.

## Mode A — first time (brain/why.md is empty)

Walk through 5 questions, ONE at a time. Don't batch. Wait for each answer.

This is the founder's **anchor**. Surface it later when they're about to quit, pivot, or rationalize away discipline.

### The questions

1. **Why this problem?** Not why you're starting a startup. Why *this* specific problem, in your own words. *Push back if the answer is generic ("I want to help founders"). Ask: what specifically about this problem makes you want to spend a decade on it?*

2. **Why YOU specifically?** Founder-market fit. Have you experienced this? Worked in this space? Have unique access to the customers? *If they say "anyone could solve this," that's a flag — push back.*

3. **What about the world is wrong because this problem exists?** Forces them to articulate the bigger picture. *If they can't answer, the problem may not matter enough.*

4. **What would you NEVER want to be true that this product solves?** Inverts the goal. Often surfaces a deeper reason than the first answer.

5. **What would make you quit?** Be specific. *"It being hard"* is not an answer. *"If 50 customer interviews showed nobody had this problem"* is an answer. *"If my co-founder leaves"* is an answer. *"If I haven't reached PMF in 2 years"* is an answer. **This is the most important question** — it defines the kill criteria for the whole startup.

### Write to `brain/why.md`

```markdown
# Why

Captured: <today's date>

## Why this problem
<their answer to Q1, verbatim>

## Why me
<Q2>

## What's wrong with the world
<Q3>

## What I never want to be true
<Q4>

## What would make me quit
<Q5 — keep this exact phrasing for later>
```

After writing, tell them: *"This file is the anchor. When you're about to quit, pivot, or rationalize away the work, run /why and I'll show this back to you. Don't edit it lightly."*

## Mode B — recall (brain/why.md exists)

Triggered when the founder:
- Asks "should I quit?"
- Wants to pivot without going through `/pivot`
- Wants to skip a stage gate
- Says they're tired or burned out
- Asks if this is worth it

Or invoked explicitly with `/why`.

### What to do

1. Read `brain/why.md` and any related entries in `brain/journey.md` (if exists)
2. Surface their own past answers back at them — verbatim, in their own words
3. Ask **one** question, depending on what triggered the recall:
   - If they're tempted to quit: *"You wrote this on [date]. Has anything changed about why this problem matters to you, or just about how hard it's been?"*
   - If they want to pivot: *"You wrote that the kill criterion was [X]. Has [X] happened, or are you pivoting because it got hard?"*
   - If they want to skip discipline: *"You wrote that you'd quit if [X]. Skipping discipline accelerates [X]. Still want to skip?"*

4. **Don't sermonize.** Don't list 10 reasons to keep going. Just hold up the mirror. Their own past words do the work.

5. End with: *"Your call. Tell me the move and I'll log it to brain/journey.md."*

### Log the moment

Whatever they decide, append to `brain/journey.md` (create if missing):

```markdown
## <date> — <one-line context>
Trigger: <why was /why invoked>
Recall surfaced: <which question's answer was most relevant>
Founder's response: <what they decided>
```

This builds a record over time of the times the founder doubted, kept going, or pivoted. By month 12, this file is the most valuable thing in the brain.

## Why this exists

Most founder failure isn't intellectual — it's emotional. The framework didn't fail; the founder ran out of *why*. If you stop loving the problem, you'll quit. Solutions are temporary; the problem is the anchor.

The `/why` skill is the founder's externalized memory of what they cared about when their head was clearest. Surfaced at the moment they need it most. The brain remembers what you forgot you knew.
