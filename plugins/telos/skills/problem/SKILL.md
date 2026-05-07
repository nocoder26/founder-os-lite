---
name: problem
description: Capture or refine the founder's problem hypothesis with Mom-Test rigor. Use at Stage 0 initial setup, or when interview signals contradict the current hypothesis.
---

# /problem

Read `brain/problem.md` (may be empty). Read `brain/why.md` if it exists.

## If `brain/problem.md` is empty (first time)

Walk the founder through ONE question at a time. Wait for each answer before moving on. Do not batch.

Vague answers now → vague product later. Push back on every vague answer — until the answer is specific enough that a stranger could find the affected user in the wild.

### The questions

1. **What's the pain — in the user's words, not your solution's?**  
   *If they answer with their solution ("can't manage finances easily"), reframe to user words ("chasing late invoices eats 6 hours/week") and ask them to confirm.*

2. **Who has it?** Specific. Not "small businesses." Industry, size, geography, role, stage. *("Service businesses, 1-10 employees, US, that invoice clients monthly.")*

3. **How often does it hit?** Daily / weekly / monthly / annually. *Frequency drives willingness to pay.*

4. **What do they do today instead?** *If "nothing," the pain isn't real enough. Real pain has workarounds.*

5. **What's the cost of the pain?** Time / money / risk / reputation. Quantify if possible.

6. **Have YOU experienced this yourself?** When? Specifically. *Founder-market fit — scratch your own itch. If no, name the closest analog.*

7. **What would prove this hypothesis WRONG?** Falsification criteria. *If we discovered X, we'd abandon this hypothesis.*

8. **Market type — existing, new, resegmented, or clone?** *Drives whole strategy. If unsure, ask: are there existing competitors with paying customers? Yes → existing. No, but adjacent → new or resegmented. Yes elsewhere, not here → clone.*

### Write to `brain/problem.md`

```markdown
# Problem hypothesis

Captured: <today's date>
Last refined: <today's date>

## Pain
<one sentence in user's words>

## Who
<specific segment>

## Frequency
<daily/weekly/monthly>

## Current alternative
<what they do today>

## Cost
<time/money/risk>

## Founder-market fit
<have you experienced it? evidence?>

## Falsification criteria
<what would make us abandon this hypothesis>

## Market type
<existing/new/resegmented/clone>
```

## If `brain/problem.md` already exists (refining)

Read recent files in `brain/interviews/`. Compare new signals to current hypothesis.

Surface contradictions explicitly:  
*"Your hypothesis says weekly frequency, but interviews 4 and 5 said daily. Your hypothesis says all SMBs, but every believer so far is a law firm. Refine, narrow, or pivot?"*

**Don't auto-update.** Make the founder choose. The act of revising the hypothesis is itself the work.

After they choose, update `brain/problem.md` with a new "Last refined" date and a `## Refinement log` entry explaining what changed and why.

## After

Suggest `/interview` as the next step.

Update `brain/stage.md` from `0` to `1` if all three are met:
- Problem hypothesis written (all 8 fields)
- Falsification criteria specified
- Founder-market fit declared

If stage advanced, congratulate them once and tell them what's next: *"Stage 1 unlocked. You can now write to `experiments/` for throwaway prototypes. `product/` is still blocked until 5 believers are identified. Start with `/interview`."*
