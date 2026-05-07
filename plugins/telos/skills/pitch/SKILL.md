---
name: pitch
description: Render brain/story.md into a 10-slide pitch deck where every claim cites a brain entry. Refuses to fabricate TAM, vanity metrics, or unsupported quotes. Flags weak slides honestly so the founder fixes them before any VC sees the deck.
---

# /pitch

Read `brain/story.md` (must exist — run `/story` first if not). Read `brain/problem.md`, `brain/believers/index.md`, `brain/interviews/`, `brain/decisions.md`, `brain/runway.md`, `brain/metrics/` (if exists).

If `brain/story.md` is empty: refuse. *"No story captured. Run /story first — the deck is downstream."*

## The deck (10 slides, YC-style)

Every slide cites specific brain entries. **Every. Single. Slide.**

### Slide 1 — Title
- Project name
- One-line tagline (from `brain/story.md` "vision" condensed)
- Founder name + handle

### Slide 2 — Problem
- 1-3 sentences from `brain/problem.md`
- ONE verbatim quote from a believer (cite interview file)
- **DO NOT** include "X% of Y have this problem" stats unless `brain/evidence/` supports it

### Slide 3 — Customer
- Segment from `brain/believers/index.md` (top concentration)
- Believer profile: pain, behavior, willingness to pay
- Cite N believers identified

### Slide 4 — Solution
- **Only** what's been validated
- For each feature: which believer asked for it (cite interview file)
- Unbuilt features marked "v1.5 (planned)" — don't pretend they exist

### Slide 5 — Traction
- Real numbers from `brain/metrics/` and `brain/believers/`
- Disappointment % if measured (from `/pmf-check`)
- Retention curve if measured
- **DO NOT** include vanity metrics (downloads, signups, MAU without retention)
- If traction is thin: write *"Pre-traction. N believers identified, MVP launching wk Y."* — admit it openly

### Slide 6 — Why now
- Founder fills. Claude prompt: *"What changed in the world that makes this possible/needed now? Be specific. Don't say 'AI is hot.'"*
- If founder can't answer, mark slide WEAK in the assessment

### Slide 7 — Team
- Founder fills. Highlight founder-market fit from `brain/why.md`
- Co-founders: name, role, why-them

### Slide 8 — Business model
- Pricing from `brain/decisions.md` if logged
- Unit economics if `/default-alive` has been run (cite `brain/runway.md`)
- If untested: mark *"Hypothesis — not yet validated."*

### Slide 9 — Vision
- 1-3 sentences from `brain/story.md` "vision"
- The changed world if this works at scale

### Slide 10 — Ask
- From `brain/story.md` "ask"
- Calibrated to `brain/runway.md`
- Specific number, specific milestone

## Output: brain/pitch/deck.md

Markdown format renderable into Keynote / Pitch.com / Slidev / Marp.

For each slide, include a `## Citations` block listing the brain entries used.

```markdown
# <Project name>

## Slide 1: Title
<...>

### Citations
- brain/story.md "vision"

---

## Slide 2: Problem
<...>

> "<verbatim quote from believer>"
> — <Name>, interview #<N>

### Citations
- brain/problem.md (current hypothesis)
- brain/interviews/00X-<name>.md

---
[...]
```

## Honest deck assessment (mandatory after rendering)

Surface weak slides explicitly. The founder needs to see the gaps before a VC does:

```
DECK ASSESSMENT:
✅ Slide 2 (Problem):    strong — 3 verbatim quotes, specific segment
✅ Slide 4 (Solution):   strong — every feature cites a believer
⚠️  Slide 5 (Traction):   WEAK — only 12 believers, no retention data
⚠️  Slide 6 (Why now):    WEAK — founder didn't fill in, currently generic
✅ Slide 8 (Business):   adequate
❌ Slide 9 (Vision):     generic — needs work before sending

VCs will probe slides 5, 6, 9. Address these before any pitch meeting.
```

## Hard refusals

- **Refuses** to write TAM if `brain/evidence/` doesn't support it. Will write *"TAM unknown — to be sized"* instead.
- **Refuses** to write *"we are growing N% MoM"* without retention data in `brain/metrics/`.
- **Refuses** to fabricate quotes. Period.
- **Refuses** to write *"the market is $X billion"* without a cited source.
- **Refuses** to call something a "platform" if `brain/decisions.md` doesn't show platform decisions.

## Why this exists

Most pitch decks are full of made-up numbers and unsupported claims. VCs detect this in 30 seconds. **The deck where every claim has a citation is rare and credible.**

You're not pitching the deck — you're pitching the story behind it. This skill makes the deck a faithful render of the story: your story, your evidence, your receipts. When a VC asks *"how did you arrive at this number?"* you have the citation ready.
