---
name: believers
description: Classify interview participants as Believer / Neutral / Infidel using the earlyvangelist test. Track believer density. Surface PMF-mirage when too many users are tire-kickers.
---

# /believers

Read all files in `brain/interviews/` and `brain/believers/index.md` (if exists).

## Three modes

Ask: *"What do you want to do — (a) review current believer roster, (b) re-classify a specific interview, or (c) check believer density and PMF signal?"*

## Mode A — Review roster

Print a clean table of all classified interviews:

```
NAME              | DATE       | SEGMENT      | CLASSIFICATION | KEY QUOTE
------------------|------------|--------------|----------------|---------------------------
Sarah K.          | 2026-04-15 | family law   | BELIEVER       | "I'd pay $50/mo tomorrow"
Mike R.           | 2026-04-18 | accounting   | NEUTRAL        | "interesting but not urgent"
...
```

Then surface:
- **Believer count** — N of M total interviews
- **Believer density** — N/M as %
- **Segment concentration** — what % of believers are in the dominant segment

If believer density < 30% across 5+ interviews: **flag PMF-mirage risk.**  
*"Out of 12 interviews, only 2 believers. 83% of your users are tire-kickers. Either your problem is real but you're talking to the wrong people, or your problem isn't real for this segment. Re-target or re-frame?"*

## Mode B — Re-classify a specific interview

Founder names the interview file. Re-run the earlyvangelist test, with the founder, against the latest evidence:

**The 5 criteria (yes/no each, with evidence):**
1. **Has the problem** — quote the line where they admit it unprompted
2. **Knows it's a problem** — quote the line where they name it specifically
3. **Has tried to solve it** — list specific workarounds, paid tools tried, hires
4. **Has budget** — what do they already spend on adjacent tools/services?
5. **Would pay** — verbatim quote where they said so (not led)

Score: **5/5 = BELIEVER. 3-4 = NEUTRAL. 0-2 = INFIDEL.**

**Important:** "would pay" must be unprompted. If founder asked *"would you pay?"* and got *"sure"*, that's not a believer signal — that's politeness. Demand the verbatim quote.

Update the interview file's `classification:` frontmatter and append a re-classification log entry.

## Mode C — Density check + PMF signal

Calculate:
- **Believer density** — believers / total interviews. *Healthy: ≥30% by interview 10. Strong: ≥50%.*
- **Segment concentration** — % of believers in the top segment. *Concentration ≥60% suggests a focused niche; <40% suggests scattered need (refine targeting).*
- **Time-to-first-believer** — how many interviews before believer #1? *>5 is a smell.*

For each metric, give a one-line read:
- *"Density 42% — solid. Continue."*
- *"Density 8% — most users are tire-kickers. Re-segment or re-frame."*
- *"Concentration 80% in family law firms — you have a niche. Lean in or expand on purpose, not by accident."*

## Why this matters

Find believers, not users. The 50-users-but-no-retention startup feels like PMF and isn't. The earlyvangelist test is the difference between feedback and signal.

A founder with 50 users and 5 believers is in better shape than a founder with 500 users and 10 believers. Density is the metric. Classification is the act of forcing yourself to be honest about who actually needs what you're building.

## Anti-pattern to call out

If the founder asks to mark someone as a Believer who failed 2+ criteria: refuse and explain why. *"Marking Mike as a Believer when he hasn't tried to solve the problem and has no budget is wishful thinking. Mark him Neutral. The honest map is the useful map."*
