---
name: pmf-check
description: Triangulate Product-Market Fit signal from three independent sources — disappointment survey, retention cohorts, believer density. Returns Strong PMF / PMF / Pre-PMF / PMF Mirage. The triangulation is what's hard to fake.
---

# /pmf-check

Read `brain/believers/index.md`, `brain/interviews/`, `brain/metrics/` (if exists), `brain/runway.md`. Use `believer_density()` from the brain MCP.

PMF is **not one number**. It's three signals that have to align. Any single signal alone is gameable. The triangulation is what's hard to fake.

## Three signals

### Signal 1 — Disappointment survey

Ask **all current users** (not cherry-picked):
> *"How would you feel if you could no longer use this product?"*

Options:
- Very disappointed
- Somewhat disappointed
- Not disappointed
- N/A — I no longer use it

**Threshold: ≥40% "very disappointed" = PMF signal.**

If founder hasn't run this:
- Generate the survey form (Google Form / Typeform / Tally — the questions, not the platform)
- Tell them to send to all active users (not just believers)
- Aim for 30+ responses minimum

If founder has results, capture in `brain/metrics/disappointment-survey.md`:

```markdown
# Disappointment survey

Captured: <date>
Sample size: <N responses>
Sent to: <user pool description — must be ALL users, not selected>

## Results
- Very disappointed: X% (N=...)
- Somewhat disappointed: Y% (N=...)
- Not disappointed: Z% (N=...)
- N/A: ...% (N=...)

## Verdict
<PASS (≥40%) / WEAK (25-39%) / FAIL (<25%)>
```

### Signal 2 — Retention cohort

Day 7, 30, 90 retention curves. **The shape matters more than the number.**

- **Flat at zero** → no PMF. Users churn completely.
- **Curve that flattens above zero** → PMF signal. Some core group keeps using it.
- **Rising curve** → exceptional, rare. (Network effects working.)

Calculate from product analytics. If founder doesn't have this set up:
- Ask for raw data (CSV: `user_id, signup_date, last_active_date`, plus weekly active flags if available)
- Compute cohort retention manually (Day 1, 7, 14, 30, 60, 90)
- Output to `brain/metrics/retention-cohorts.md`

Verdict: **PASS** (curve flattens >0%), **WEAK** (asymptote near zero), **FAIL** (everyone gone by Day 30).

### Signal 3 — Believer density (from /believers)

Run `/believers` if not recently run. Use `believer_density()` from brain MCP.

- **<15%** → PMF mirage (most users are tire-kickers)
- **15–30%** → weak; refine targeting
- **30–50%** → healthy
- **≥50%** → strong, focused niche

Verdict: **PASS** (≥30%), **WEAK** (15-29%), **FAIL** (<15%).

## Triangulation

Mark each signal:

```
                | Threshold        | Actual   | Verdict
----------------|------------------|----------|--------
Disappointment  | ≥40%             | __%      | ____
Retention       | curve flattens   | ____     | ____
Believer dens   | ≥30%             | __%      | ____
```

## Final verdicts

- **3 of 3 PASS → STRONG PMF.** Stage 2 → 3 gate met. Time to scale. Run `/default-alive` and `/story`; raise if needed.
- **2 of 3 PASS → PMF.** Real signal but specific weakness. Fix the FAIL before scaling.
- **1 of 3 PASS → Pre-PMF.** Early. Keep iterating in Stage 2. Don't scale yet.
- **0 PASS, or only believer density passes → PMF MIRAGE.** Most dangerous state. Feels like PMF but isn't. Vanity metric pattern. Re-target or refine hypothesis.

## Output: brain/metrics/pmf-check.md

```markdown
# PMF check

Captured: <date>

## Disappointment survey
<copy of brain/metrics/disappointment-survey.md results>
Verdict: ___

## Retention
<cohort table>
Verdict: ___

## Believer density
<from believer_density()>
Verdict: ___

## Triangulation
<2 of 3 / 3 of 3 / etc.>
**Final: <Strong PMF / PMF / Pre-PMF / PMF Mirage>**

## Action
<one of: scale / address weakness X / iterate / re-target>
```

## Anti-patterns to call out

- **"I have 1000 signups" alone is not PMF** — *"Users without retention is acquisition, not PMF."*
- **Survey from cherry-picked users** — *"Must be ALL active users, not selected ones. Otherwise the bias makes it noise."*
- **Founder claims PMF before this skill runs** — *"PMF is the triangulation, not the vibe. Run the three checks."*
- **One signal screaming, two silent** — *"That's a vanity metric, not PMF. The triangulation is the safeguard."*

## Why this exists

Vanity metrics feel like progress; actionable metrics tell the truth. Until disappointment hits ≥40%, scaling acquisition is multiplying churn. Most founders think they have PMF when one user says something nice — real PMF is when most users would be heartbroken if you shut down.

This skill is the reality check before the scaling decision.

After `/pmf-check` returns Strong PMF: stage gate to 3 unlocks. Run `/default-alive` next to check whether you can fund the scale-up.
