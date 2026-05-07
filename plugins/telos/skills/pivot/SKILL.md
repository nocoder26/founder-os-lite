---
name: pivot
description: Walk through the 10 canonical pivot types using brain evidence to inform direction. Forces explicit kill criteria for the previous hypothesis before allowing a pivot. Logs to brain/pivots.md with full reasoning.
---

# /pivot

Read `brain/problem.md`, `brain/believers/index.md`, `brain/interviews/`, `brain/decisions.md`, `brain/pivots.md` (if exists). Run `query_evidence()` for relevant signals.

## When to invoke

Founder is considering changing direction. Triggers:
- Believer density <30% after 5+ interviews
- Retention curve approaching zero
- Multiple "this isn't quite my problem" signals
- Founder explicitly says *"I'm thinking about pivoting"*

## Step 1 — Surface what's actually wrong

Before naming a pivot type, name the failure. Read brain/ and ask:
- What did the original hypothesis predict?
- What did the evidence show?
- Where exactly did they diverge?

If the founder hasn't done a `/problem` refresh recently, suggest it before pivoting. Often the "pivot" is just a refinement.

## Step 2 — Walk through the 10 canonical pivot types

For each, ask: *"Does this match what your evidence is telling you?"* Cite brain entries as you go.

1. **Zoom-in pivot** — A single feature becomes the whole product.
   *Evidence pattern: users love ONE thing, ignore the rest.*
2. **Zoom-out pivot** — The whole product becomes a single feature of something larger.
   *Evidence pattern: users want it as part of an existing workflow, not standalone.*
3. **Customer segment pivot** — Same product/problem, different customer.
   *Evidence: wrong people responding well to right solution.*
4. **Customer need pivot** — Same customer, different problem.
   *Evidence: customer engaged but not on the pain you targeted.*
5. **Platform pivot** — Application ↔ platform.
   *Evidence: developers want APIs, or customers want a turnkey app.*
6. **Business architecture pivot** — B2B ↔ B2C, or high-margin/low-volume ↔ low-margin/high-volume.
   *Evidence: monetization model mismatch with how the segment buys.*
7. **Value capture pivot** — Different monetization model.
   *Evidence: willingness-to-pay exists but not for the model you priced.*
8. **Engine of growth pivot** — Sticky / viral / paid (the three canonical growth engines).
   *Evidence: growth working through a different mechanism than designed for.*
9. **Channel pivot** — Same product, different distribution.
   *Evidence: customers prefer to buy/discover differently than you offer.*
10. **Technology pivot** — Same customer/problem, different tech.
    *Evidence: you can deliver the same value cheaper/faster/better with new tech.*

## Step 3 — Kill criteria for the OLD hypothesis (non-negotiable)

Before any pivot, force the founder to write down:
- What was the original hypothesis?
- What evidence proved it wrong (cite specific interview / metrics)?
- Why are we sure it's wrong, not just early?

Pivots without explicit kill criteria are noise. **Refuse to log the pivot until these are written down.**

## Step 4 — New hypothesis with falsification

The pivot is a NEW hypothesis. It needs:
- Specific customer segment
- Specific pain
- Falsification criteria (what would prove THIS wrong)

Run `/problem` on the new hypothesis. **Don't auto-overwrite the old one** — preserve history. Old `problem.md` becomes part of the pivot log.

## Step 5 — Log to brain/pivots.md

Append:

```markdown
## <date> — <pivot type>: <one-liner>

### Old hypothesis (killed)
<copy of brain/problem.md before pivot>

### Kill criteria met
- <specific evidence — interview ref, metric, quote>
- <...>

### Pivot type (Ries)
<one of 10>

### New hypothesis
<see brain/problem.md as of this date>

### What carries over
- Believers willing to follow: <names>
- Evidence still relevant: <ref>

### What we lose
- <ref>

### Reasoning
<one paragraph — what we learned, what we believe now, what we'll watch>
```

## Anti-pattern to call out

If founder wants to pivot every 2 weeks: this is thrash, not pivoting. Surface `brain/pivots.md` history. *"You've pivoted twice in 8 weeks. The problem is probably not the hypothesis — it's that you're not running long enough experiments to learn from any of them. Either let this one run another 4 weeks, or admit it's not the hypothesis you're rejecting — it's the discomfort of a hypothesis without quick wins."*

## Why this exists

A pivot is a structured course correction designed to test a new fundamental hypothesis about the product, strategy, and engine of growth.

Most founders pivot in panic. This skill makes pivots **structured, evidence-driven, and historical** — the brain remembers every old hypothesis and why it was killed. Future-you reads pivots.md and sees the trail of validated learning, not just the latest narrative.

It's only a pivot if you can articulate what was wrong. Otherwise it's a fresh start — which is fine, just call it that.
