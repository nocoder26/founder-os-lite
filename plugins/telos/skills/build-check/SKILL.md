---
name: build-check
description: Before adding a feature, query brain/evidence/ for matching customer signals. Returns GREEN (clear evidence), AMBER (related signal), or RED (no evidence). Use before any non-trivial product change.
---

# /build-check

Take a feature description as input. If founder didn't include one, ask: *"What feature are you considering? One sentence."*

## Read brain state

- `brain/stage.md` — what stage are we in
- `brain/problem.md` — current hypothesis
- `brain/evidence/` — all atomic signals
- `brain/interviews/` — full interviews for context
- `brain/believers/index.md` — who are our believers

## Stage-aware behavior

**Stage 0 (Pre-Discovery):** refuse outright. *"You don't have a problem hypothesis yet. There's nothing to build. Run `/problem`."*

**Stage 1 (Discovery):** allow only if the feature is for an `experiments/` throwaway prototype. *"You're in Discovery. Real product comes after 5 believers. Want to scope this as a 100-line throwaway in `experiments/` to test the hypothesis?"*

**Stage 2+ (Validation onward):** run the full evidence check below.

## The evidence check (Stage 2+)

Compare the proposed feature against all signals in `brain/evidence/` and quotes in `brain/interviews/`. Return one of three verdicts:

### 🟢 GREEN — evidence supports building

At least one believer explicitly named this need. Verbatim quote exists. Behavior observed (already paid for adjacent tool, manual workaround documented).

Output:
```
🟢 GREEN — build with confidence

Evidence:
- Sarah K. (BELIEVER, interview #4): "I'd pay $50/mo tomorrow for [exact thing]"
- Mike R. (BELIEVER, interview #7): tried 3 workarounds in 6 months
- Behavior: 60% of believers spend ≥3hr/week on this manually

Linked decision logged to brain/decisions.md.
```

Append to `brain/decisions.md`:
```markdown
## <date> — <feature one-liner>
Evidence: <interview refs>
Decision: build
```

### 🟡 AMBER — related signal, not direct

Believers mention the *area* but not this specific feature. Or the evidence is one-sided (single believer, or weak quote).

Output:
```
🟡 AMBER — build cautiously, or ask one more believer first

Closest evidence:
- Sarah K. mentioned "[adjacent thing]" but not this specific feature
- 1 of 5 believers in this segment

Recommendations:
1. Run /interview with one more believer asking specifically about [this feature]
2. OR scope this as an experiment, not product code
3. OR build it but log as 'speculative' in brain/decisions.md
```

### 🔴 RED — no evidence

No believer mentioned anything close. Pure founder intuition.

Output:
```
🔴 RED — no believer evidence supports this

What I searched: <terms>
What I found: nothing matching

This is solution-thinking, not problem-thinking. Three options:

1. Talk to a believer specifically about this. Run /interview with the right question.
2. Drop the feature.
3. Build in experiments/ as a 100-line throwaway, not product/.

Building this now in product/ is how you ship the wrong thing for 4 weeks.
```

## Special case: founder pushes back

If founder says *"I just know this is right"* or *"trust me"*: hold the line gently.

*"That might be true. But the goal of Telos isn't to second-guess your taste — it's to make sure your taste is informed by what believers actually need. If you're confident, run one /interview to confirm. 30 minutes saves 4 weeks if you're wrong, costs 30 minutes if you're right."*

If they still want to skip: log to `brain/decisions.md` with status `MANUAL_OVERRIDE` and the founder's stated reasoning. Don't refuse — but make the override visible.

## Why this exists

Most founders ship the wrong product because their tools say yes too easily. Cursor, Copilot, Claude Code-as-yes-machine — they help you build whatever you ask for, fast. That's a problem when "what you ask for" isn't grounded in what users actually need.

`/build-check` is the friction point. Half the time you'll have evidence and ship. The other half you'll save weeks.
