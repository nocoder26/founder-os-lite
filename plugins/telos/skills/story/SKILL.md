---
name: story
description: Construct the founder's narrative arc — origin, why-you, journey, vision, ask. Reads brain/why.md and brain/ for cited evidence. Output feeds /pitch downstream. Every claim cites a brain entry.
---

# /story

Read `brain/why.md`, `brain/problem.md`, `brain/interviews/`, `brain/believers/index.md`, `brain/decisions.md`, `brain/pivots.md` (if exists), `brain/runway.md` (if exists).

If `brain/why.md` is empty: refuse. *"No /why captured. Run /why first — the founder's anchor is the spine of every story."*

## The arc — five acts

Pitching is storytelling. The story has 5 acts. The deck is downstream.

This skill builds the **story** — the deck (`/pitch`) renders it.

### Act 1 — Origin
*"What did you see that nobody else saw?"*

Pull from `brain/why.md`: the founder's specific lens. The moment they noticed the problem.

If `brain/why.md` is generic, push back: *"Your /why says 'I want to help small businesses.' That's not an origin story. What specific moment made YOU notice this problem?"*

### Act 2 — Why you
*"Why are you the one to solve this?"*

Founder-market fit. Pull from `brain/why.md` (Q2 — *"why you"*). Surface specific qualifications: lived expertise, prior work, unique access to the customer base.

### Act 3 — The journey (the proof)
*"What have you learned?"*

This is where validated learning becomes story. Pull from:
- `brain/interviews/` — verbatim quotes from believers
- `brain/believers/index.md` — segment patterns
- `brain/decisions.md` — the calls you made and why
- `brain/pivots.md` — the times you were wrong and how you knew

The journey arc is: *"I thought X. Talked to N people. Learned Y. Refined to Z. Believers now look like this."*

**Include the failures.** Real journeys have pivots. Surfacing them makes the rest credible.

### Act 4 — The vision
*"Where does this go?"*

The future state. **Not the feature roadmap.** The world that exists if this works.

Push back if vague: *"'A platform for X' is not a vision. What changes for the customer? Be specific. Make it sensory."*

### Act 5 — The ask
*"What do you need next?"*

Specific. Time-bound. Linked to the journey:
- *"I need [N months runway / Y customers / Z hires] to reach [next validated milestone]."*

Pull from `brain/runway.md` if available — the ask should be calibrated to actual default-alive math, not aspiration.

## Output: brain/story.md

```markdown
# Story

Captured: <date>
Last refined: <date>

## Origin
<2-3 paragraphs — the moment you saw it>

## Why you
<1-2 paragraphs — founder-market fit>

## The journey
<3-5 paragraphs — what you've validated, with verbatim quotes from interviews>

## Vision
<1-2 paragraphs — the changed world>

## Ask
<1 paragraph — specific, time-bound, milestone-linked>

## Citations
- Interview #001 (Sarah K.): "..."
- Interview #004 (Jen M.): "..."
- Decision 2026-04-15: pivoted to law firm vertical because...
- Pivot 2026-04-22 (customer segment): evidence: ...
```

## Important rules

1. **Every claim cites a brain entry.** No fabricated quotes. No invented stats.
2. **The story is YOURS, in your voice.** I structure it; you say the words. Don't let me write platitudes.
3. **If a section is thin, say so explicitly.** *"Vision needs work — currently weak. Fill in before /pitch."* Don't paper over gaps with prose.
4. **Don't make the journey heroic.** Real journeys have failed pivots, awkward learnings, doubt. Include those — they make the story credible.

## Why this exists

Fundraising is storytelling. If you can't tell the story, you can't raise.

Most founder pitches are decks of bullet points. The deck is downstream of the story. **Build the story first.** Then `/pitch` renders it.

After `/story`: run `/pitch` to render slides.
