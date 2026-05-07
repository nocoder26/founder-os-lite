---
name: default-alive
description: Calculate runway, growth rate, and default alive vs default dead status. Required before any new spend or hire. Surfaces the brutal math founders avoid.
---

# /default-alive

Read `brain/runway.md`. If empty or stale (>30 days old), capture inputs first.

## Capture inputs (if needed)

Ask one at a time:

1. **Current cash on hand** — bank balance + receivables that'll definitely arrive in 30 days
2. **Monthly burn rate** — total monthly spend (salaries, infra, tools, contractors)
3. **Current monthly revenue** — actual collected revenue, not pipeline or MRR projections
4. **Monthly revenue growth rate** — average over last 3 months. Honest math: if last month was $1000 and the month before was $800, that's 25%/mo. Don't smooth.
5. **Cost growth rate** — are you adding burn each month? Hires, infra scaling.

If any field can't be answered confidently, refuse to give a verdict: *"Can't tell you if you're default alive without honest numbers. The temptation to flatter the inputs is the most dangerous part of this calculation. Get real numbers, then come back."*

## Write to `brain/runway.md`

```markdown
# Runway state

Captured: <date>

## Cash on hand
$<X>

## Monthly burn
$<Y>

## Monthly revenue
$<Z>

## Revenue growth (3-mo avg)
<G>%/month

## Burn growth
<B>%/month (or "flat")

## Source of numbers
<bank statement / Stripe export / etc.>
```

## Calculate

**Months of runway at current burn (no growth):**
```
runway = cash / (burn - revenue)
```
If `revenue >= burn`, you're profitable — return *"Profitable. Default alive trivially. Nice."* and stop.

**Default alive check:**

> A startup is default alive if, at its current rate of growth, its profits will exceed its costs before it runs out of money.

Project month-over-month: revenue growing at G%/month, costs growing at B%/month, until one of:
- Revenue exceeds costs (→ default alive)
- Cash runs out (→ default dead)

Run the projection until one fires. Show the table:

```
Month | Revenue   | Burn      | Net burn  | Cash     
------|-----------|-----------|-----------|----------
0     | $5,000    | $40,000   | $35,000   | $300,000 
1     | $6,000    | $40,800   | $34,800   | $265,200 
2     | $7,200    | $41,616   | $34,416   | $230,784 
...
```

## Return the verdict

### 🟢 DEFAULT ALIVE

*"At current growth (X%/mo) and burn (Y%/mo), revenue covers costs in month N, before runway zeros at month M. You're default alive. Don't get cocky — growth rates regress. Re-run this monthly."*

### 🔴 DEFAULT DEAD

*"At current growth (X%/mo), you hit zero in month N before revenue covers costs. You're default dead.*

*Three options, in order of preference:*
1. *Cut burn — what's the largest line item? Can it go?*
2. *Grow faster — what's the highest-leverage thing for revenue this week?*
3. *Raise — but only if (1) and (2) are exhausted. Investors fund growth, not survival.*

*Pick one. If you do nothing, you have N months."*

### 🟡 BORDERLINE

If the math is close (default alive only if growth holds, dead if it dips 20%): flag it.

*"Borderline. You're default alive only if growth holds at X%/mo. A single bad month flips you to dead. Plan for both — what's the cut list ready if next month's growth is half?"*

## Special prompts

**If founder asks to skip:** *"Refusing to look at runway is how startups die surprised. Two minutes."*

**If numbers feel manufactured:** push back. *"Revenue growth at 40%/mo from $200 base is not a trend yet. Three months of data minimum. What did month 1 actually do?"*

**Before any hire request:** auto-run this skill. *"Hiring adds $X to monthly burn. Re-run runway with the new burn before saying yes."*

## Why this exists

Founders avoid runway math because the answers are scary. The cost of avoidance is dying surprised at month N+1 when the credit card bounces. Default dead is the most common founder failure mode that's solvable two months earlier than it gets discovered.

Run this monthly. Always.
