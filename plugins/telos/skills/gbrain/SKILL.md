---
name: gbrain
description: Optional bridge — sync Telos's brain/ folder into a gbrain MCP instance so interviews, believers, decisions, and pivots become queryable, linked, and citable across projects. Telos works perfectly without this; gbrain integration is purely additive. Hard-refuses if gbrain MCP is not detected. Idempotent, never silently overwrites, requires explicit opt-in per category, leaves an audit trail in brain/integrations/gbrain-log.md.
---

# /gbrain — bridge Telos brain/ into gbrain

This is an **optional** skill. Telos works perfectly without it. If you have gbrain installed (Garry Tan's brain MCP — github.com/garrytan/gbrain), this skill turns your `brain/` folder into linked, queryable gbrain pages so:

- You can search across all your interviews ("what do I know about onboarding friction?")
- Decisions cite specific interview pages (backlinks shown automatically)
- Believer roster is filterable by tag, segment, status
- Knowledge persists across multiple Telos projects in one searchable graph

Telos remains the source of truth. gbrain becomes the queryable index.

## Pre-flight refusals (non-negotiable)

Refuse hard if any are true:

1. gbrain MCP is not available — call `mcp__brain__get_health`. If it errors or returns no response, refuse: *"gbrain MCP not detected. Install from github.com/garrytan/gbrain first, ensure it's in your `.mcp.json`, then retry. Telos works fine without it — this skill is purely additive."*
2. `brain/` folder doesn't exist — *"No Telos brain/ to sync. Run /telos:start or /telos:why first."*
3. Founder hasn't run `setup` mode in this project — refuse all sync operations until setup completes. Setup is one-time and registers the project in gbrain with the right schema.

## Modes

```
/telos:gbrain setup            — first-time setup; registers schema and conventions
/telos:gbrain status           — show what's synced, what's drifted, what's missing
/telos:gbrain sync interviews  — sync brain/interviews/ to gbrain
/telos:gbrain sync believers   — sync brain/believers/index.md to gbrain
/telos:gbrain sync decisions   — sync brain/decisions.md
/telos:gbrain sync pivots      — sync brain/pivots.md
/telos:gbrain sync all         — bulk sync all categories (with per-category confirmation)
/telos:gbrain unlink           — remove gbrain references from brain/ files (does NOT delete gbrain pages — that's gbrain's responsibility)
/telos:gbrain force-overwrite <slug> — explicit destructive override for a CONFLICT page (use only when you're sure the local source is canonical)
/telos:gbrain pull <slug>      — fetch a CONFLICT'd gbrain page back to local for manual merge
```

Default mode if invoked bare (`/telos:gbrain`): print `status`, then prompt the founder to pick an action.

---

## Mode 1 — `setup` (one-time, required before any sync)

1. Verify gbrain health (`mcp__brain__get_health`). Refuse if not OK.
2. Read `brain/why.md` and `brain/problem.md` to extract project metadata.
3. Generate a project slug: `telos-project-<slugified-from-problem-Q1-segment>` (e.g., `telos-project-smb-services-firms`).
4. Check if that slug exists in gbrain (`mcp__brain__get_page` with the slug). If yes:
   - If page has tag `telos-managed` → reuse it
   - If page has tag `telos-managed` but with a different Telos source path → conflict; refuse and ask founder to pick a new slug or unlink old project
   - If no `telos-managed` tag → refuse to claim, propose appending a suffix
5. If page doesn't exist, create it via `mcp__brain__put_page`:
   ```
   slug: telos-project-<segment-slug>
   title: Telos: <one-line from problem.md>
   tags: [telos, telos-managed, telos-project, <stage-tag>]
   content: <project-overview markdown including hypothesis, stage, anchor link>
   ```
6. Write to `brain/integrations/gbrain.yaml`:
   ```yaml
   project_slug: telos-project-<segment-slug>
   gbrain_version: <from get_health response>
   telos_version: 0.0.0
   setup_at: <ISO timestamp>
   conventions:
     interview_slug_pattern: telos-interview-{date}-{participant-slug}
     believer_slug_pattern: telos-believer-{participant-slug}
     decision_slug_pattern: telos-decision-{date}-{decision-slug}
     pivot_slug_pattern: telos-pivot-{date}-{pivot-type}
     required_tags: [telos, telos-managed]
   ```
7. Initialize the audit log at `brain/integrations/gbrain-log.md` with this header:
   ```markdown
   # gbrain integration log

   This file tracks every sync action between Telos brain/ and gbrain.
   Do not edit manually — managed by /telos:gbrain.

   ## <timestamp> — setup
   Project slug: <slug>
   gbrain version: <version>
   ```
8. Report success and next steps: *"Setup complete. Run `/telos:gbrain sync interviews` to push your interview history into gbrain."*

### Resilience rules for setup

- If `get_health` succeeds but `put_page` fails → roll back: don't write the gbrain.yaml. The setup is atomic.
- If gbrain.yaml already exists with a different project_slug → don't overwrite; refuse and ask the founder to either keep using the old slug or run `unlink` first.
- If the project slug is taken by a non-telos page → propose 3 alternative slugs, let founder pick.

---

## Mode 2 — `sync interviews` (the main value loop)

This is the most important sync mode — interviews become queryable, citable customer signal that compounds across projects.

### Step 1 — Pre-flight

1. Read `brain/integrations/gbrain.yaml`. If missing, refuse and instruct to run `setup` first.
2. Verify gbrain health. If degraded, refuse with the gbrain status message.
3. List all `*.md` files in `brain/interviews/` (excluding `.gitkeep` and any subdirectories like `scripts/`).
4. If 0 files, refuse: *"No interviews to sync."*

### Step 2 — Plan the sync (dry-run logic)

For each interview file, classify into one of:

- **NEW** — no `<!-- gbrain: ... -->` tag in the file → will create a new gbrain page
- **UP-TO-DATE** — tag exists, file mtime ≤ last sync mtime in audit log → no action needed
- **MODIFIED** — tag exists, file mtime > last sync → will update the gbrain page
- **CONFLICT** — tag exists, but `mcp__brain__get_page` returns content the founder has manually edited in gbrain (detect via a content-hash field in front-matter that gbrain page has but doesn't match the source's hash) → refuse to overwrite this one; flag for review
- **MISSING** — tag exists, but `mcp__brain__get_page` returns 404 → page was deleted in gbrain; ask founder if they want to recreate or remove the local tag

Print a summary table:

```
File                                      | Status      | Slug
2026-04-29-jen-m-design.md                | UP-TO-DATE  | telos-interview-2026-04-29-jen-m-design
2026-05-02-mike-r-law.md                  | NEW         | telos-interview-2026-05-02-mike-r-law
2026-04-15-sarah-k-accounting.md          | MODIFIED    | telos-interview-2026-04-15-sarah-k-accounting
2026-03-10-old-interview.md               | CONFLICT    | telos-interview-2026-03-10-old-interview
                                          |             |    (manually edited in gbrain — review before overwriting)
```

Wait for founder confirmation: *"Proceed with sync? NEW + MODIFIED only [y], skip all [n], handle CONFLICT manually [c]."*

### Step 3 — Execute the sync (per-file)

For each file marked NEW or MODIFIED:

1. Read the file content.
2. Compute SHA-256 of content. Store in front-matter as `source_hash`.
3. Generate the slug per the convention in gbrain.yaml.
4. Build the gbrain page payload:
   ```
   slug: telos-interview-<date>-<participant-slug>
   title: <participant name + role from interview header>
   tags: [telos, telos-managed, telos-interview, <segment>, <classification-if-known>]
   front_matter:
     source: brain/interviews/<filename>
     source_hash: <sha-256>
     captured: <date from interview>
     telos_version: 0.0.0
     synced_at: <ISO timestamp>
   content: <interview markdown body>
   ```
5. Add anonymization step (if user opted in via flag): replace participant real name with `[Customer A]` style pseudonym, but preserve the mapping locally in `brain/integrations/gbrain-anonymization.json` so gbrain page is anonymized but local file isn't.
6. Call `mcp__brain__put_page` with the payload.
7. Add tags via `mcp__brain__add_tag` (in case put_page didn't take them — defensive).
8. Add a backlink to the project page via `mcp__brain__add_link(from=interview_slug, to=project_slug, type="part-of")`.
9. If the interview's hypothesis matches a believer, add a link to the believer's page (sync believers first if not done).
10. Write back to the source file: prepend `<!-- gbrain: <slug> · synced <timestamp> · hash <sha256-prefix> -->` as the second line (after any existing front-matter).
11. Append to the audit log:
    ```markdown
    ## <timestamp> — sync interview
    File: brain/interviews/<filename>
    Slug: <slug>
    Action: NEW (or MODIFIED)
    Hash: <sha256-prefix>
    ```

### Step 4 — Per-file error handling

If `mcp__brain__put_page` fails:

1. Retry once with 2-second backoff.
2. If second attempt fails, log the error to `brain/integrations/gbrain-log.md`:
   ```markdown
   ## <timestamp> — ERROR sync interview
   File: <filename>
   Slug: <attempted slug>
   Error: <error message verbatim>
   ```
3. **Continue with the next file.** A single failed sync must not abort the whole batch.
4. After all files attempted, print error summary: *"Synced X of Y. Z failed. See brain/integrations/gbrain-log.md."*

### Step 5 — Post-sync verification

After all syncs complete:

1. For each successful sync, call `mcp__brain__get_page(slug)` and verify the returned `source_hash` matches what we wrote. If mismatch, log a warning.
2. Print summary:
   ```
   ✓ Synced 3 interviews
   ✓ All hashes verified
   ⚠ 1 conflict skipped (review brain/interviews/2026-03-10-old-interview.md)
   ```
3. Suggest next action: *"Run `/telos:gbrain sync believers` next, or query gbrain to test."*

---

## Mode 3 — `sync believers`

Same pattern as interviews:
- Pre-flight: gbrain health, gbrain.yaml present, brain/believers/index.md exists
- Parse the believers index, one entry per believer
- Generate slug per convention
- Each believer page links back to the interview pages where they appear
- Each believer page tagged with status (`believer`, `neutral`, `infidel`)
- Same hash + audit trail pattern

## Mode 4 — `sync decisions` and Mode 5 — `sync pivots`

Same pattern. Decisions reference the interviews and believers that informed them. Pivots reference the killed hypothesis page (if Telos has been used long enough to have evolved the problem).

## Mode 6 — `sync all`

Sequence:
1. setup (skip if already done)
2. sync interviews
3. sync believers (depends on interviews — needs the links)
4. sync decisions (depends on interviews + believers)
5. sync pivots (depends on decisions)

Each step prompts for confirmation. If any step is declined, downstream steps that depend on it are skipped (with explanation).

---

## Mode 7 — `status`

1. Read `brain/integrations/gbrain.yaml`. If missing, report "Not set up — run `/telos:gbrain setup`."
2. Verify gbrain health. Report version + status.
3. List all `brain/<category>/` files and classify each as NEW / UP-TO-DATE / MODIFIED / CONFLICT / MISSING (per the criteria in `sync interviews`).
4. Print a per-category table:
   ```
   Category    | Total | UP-TO-DATE | NEW | MODIFIED | CONFLICT | MISSING
   interviews  |    7  |          5 |  2  |        0 |        0 |       0
   believers   |    3  |          2 |  1  |        0 |        0 |       0
   decisions   |    4  |          3 |  0  |        1 |        0 |       0
   pivots      |    1  |          1 |  0  |        0 |        0 |       0
   ```
5. Recommend the next action.

---

## Mode 8 — `unlink`

Removes the gbrain references from local brain/ files. Does NOT delete pages from gbrain — that's gbrain's responsibility (use gbrain's own delete tools).

1. Confirm: *"This will remove gbrain tags from N files in brain/. The gbrain pages themselves will NOT be deleted — use gbrain's tools for that. Continue? [y/N]"*
2. For each file with a `<!-- gbrain: ... -->` tag, remove the tag line.
3. Move `brain/integrations/gbrain.yaml` to `brain/integrations/gbrain.yaml.unlinked-<timestamp>` (preserves history without active config).
4. Append to audit log.

---

## Resilience checklist (these are the design invariants)

| # | Invariant | How enforced |
|---|-----------|--------------|
| 1 | Telos works without gbrain | Skill is opt-in; no other Telos skill imports or depends on this one |
| 2 | gbrain absence is detected | `get_health` is the first call; refuses cleanly if it fails |
| 3 | Idempotent — safe to re-run | Hash-based change detection; UP-TO-DATE files skipped |
| 4 | No silent overwrites | CONFLICT detection refuses to overwrite gbrain-edited pages |
| 5 | Atomic setup | gbrain.yaml only written if `put_page` for project page succeeds |
| 6 | Per-file failure isolation | One failed sync logs and continues; doesn't abort batch |
| 7 | Audit trail for every action | brain/integrations/gbrain-log.md tracks all syncs and errors |
| 8 | Reverse linking | gbrain slug written back to source file as comment |
| 9 | Schema versioning | gbrain.yaml records gbrain + Telos versions for future migrations |
| 10 | Privacy preserved | Optional anonymization with local-only mapping file |
| 11 | Hash verification | Post-sync, fetch page back and verify `source_hash` matches |
| 12 | Reversible | `unlink` cleanly removes Telos's footprint from brain/ files |
| 13 | Schema conventions documented | brain/integrations/gbrain.yaml is human-readable + version-controlled |
| 14 | Project slug conflicts handled | Won't claim a non-Telos page; proposes alternatives |
| 15 | gbrain page deletion handled | MISSING status flagged; user chooses to recreate or unlink |

## What this skill explicitly does NOT do

- Does not replace `brain/` as the source of truth — gbrain is the index, not the canonical store
- Does not delete gbrain pages (that's gbrain's responsibility — don't cross authority boundaries)
- Does not auto-sync on every interview save (would be intrusive; manual run is the discipline)
- Does not modify gbrain pages that weren't created by Telos (no `telos-managed` tag = hands off)
- Does not require gbrain to be running on the same machine — works against any reachable gbrain MCP

## Why this exists

Telos's brain/ is just markdown — portable, simple, git-tracked. That's the right design for the source of truth. But markdown alone doesn't compound across projects. After 3 startups and 60+ interviews, you should be able to ask: *"what do I already know about onboarding friction in B2B SaaS?"* and get verbatim quotes from interviews you forgot you ran.

gbrain is built exactly for that compounding. By bridging Telos's brain/ into gbrain, the validation work you do this year remains discoverable next year, on the next startup, in a different stack.

The integration is opt-in because Telos's core promise is "no dependencies, just markdown." This skill respects that — gbrain is a power-user upgrade, not a requirement.

## Inspired by

Built on [gbrain](https://github.com/garrytan/gbrain) by Garry Tan. The `brain-ops`, `signal-detector`, and `citation-fixer` patterns in gbrain are excellent prior art — this skill aims to play nice with those conventions, not reinvent them.

Also inspired by [gstack](https://github.com/garrytan/gstack) — Garry's broader skillpack for Claude Code engineering workflow. Telos is meant to compose with both.
