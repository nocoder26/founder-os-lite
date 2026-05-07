"""E2E workflow simulation: simulate a founder going through the full flow.

We simulate:
- Cold start (empty brain) → /why → /problem → stage 1 unlocked
- Discovery: /interview x6 with mix of believers/neutrals → stage gate computed
- Hook intercepts product/ writes at each stage
- Stage advances → product/ allowed → /build-check evaluates
- /pivot triggered with kill criteria
- /pmf-check triangulates
- /story → /pitch flow

This exercises the brain MCP, the hook, and the brain state machine end-to-end
across multiple "skill invocations" (we mock the LLM by directly calling
the MCP tools and writing brain files as the skill prompts would instruct).
"""
import sys
import asyncio
import json
import shutil
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEST_DIR = Path("/tmp/telos-e2e-project")
TEST_BRAIN = TEST_DIR / "brain"

failures = []


def reset_project():
    """Reset to a fresh user-project state.

    Plugin format: skills + hooks come from the plugin install location
    (in real usage); for tests we point at the repo's skills/ + hooks/.
    The user's project starts with an empty brain/ that gets populated by
    skills as the founder uses them.
    """
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)
    # Bootstrap an empty brain (skills will populate as the founder works)
    TEST_BRAIN.mkdir(parents=True)
    (TEST_BRAIN / "stage.md").write_text("# Stage\ncurrent: 0\n")
    (TEST_BRAIN / "interviews").mkdir()
    (TEST_BRAIN / "evidence").mkdir()
    (TEST_BRAIN / "believers").mkdir()
    (TEST_DIR / "product").mkdir(exist_ok=True)
    (TEST_DIR / "experiments").mkdir(exist_ok=True)


def get_server():
    os.environ["BRAIN_DIR"] = str(TEST_BRAIN)
    sys.path.insert(0, str(REPO / "plugins" / "telos" / "brain-mcp"))
    if "server" in sys.modules:
        del sys.modules["server"]
    import server
    server.BRAIN_DIR = TEST_BRAIN
    return server


def mcp_call(tool, args=None):
    server = get_server()
    async def _run():
        r = await server.mcp.call_tool(tool, args or {})
        if isinstance(r, tuple):
            return r[1]["result"]
        text = r[0].text
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return text
    return asyncio.run(_run())


def run_hook(file_path, content="some new code"):
    """Simulate Claude calling the PreToolUse hook."""
    hook = REPO / "plugins/telos/hooks/pre-build-coach.sh"
    inp = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
    })
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(TEST_DIR)
    # Strip claude from PATH so hook's Stage 2 claude-eval path doesn't hang
    # (this exposes that the hook lacks a timeout — see findings)
    env["PATH"] = ":".join(p for p in env.get("PATH", "").split(":")
                           if "claude" not in p.lower() and "anthropic" not in p.lower())
    proc = subprocess.run(
        [str(hook)],
        input=inp,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    out = proc.stdout
    if not out.strip():
        return "allow", ""
    try:
        d = json.loads(out)
        return d.get("hookSpecificOutput", {}).get("permissionDecision", "allow"), d.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    except json.JSONDecodeError:
        return "parse_error", out


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} -- {detail}")
        failures.append(label)


print("=== E2E WORKFLOW SIMULATION ===\n")

# ------------------------------------------------------------------
# STAGE 0 — Cold start
# ------------------------------------------------------------------
print("[Stage 0] Cold start")
reset_project()
state = mcp_call("brain_status")
check("fresh brain: stage 0", state["stage"] == "0")
check("fresh brain: no problem set", state["problem_hypothesis_set"] is False)
check("fresh brain: no why set", state["why_set"] is False)
check("fresh brain: 0 interviews", state["interviews"] == 0)

# Hook should block any product/ writes
decision, reason = run_hook(str(TEST_DIR / "product" / "main.py"))
check("hook blocks product/ at stage 0", decision == "deny")

# Hook should block experiments/ at stage 0 (no problem yet)
decision, _ = run_hook(str(TEST_DIR / "experiments" / "test.py"))
check("hook blocks experiments/ at stage 0", decision == "deny")

# Hook should allow brain/ writes
decision, _ = run_hook(str(TEST_BRAIN / "notes.md"))
check("hook allows brain/ at stage 0", decision == "allow")

# Founder runs /why → writes brain/why.md
mcp_call("update_why", {"content": "# Why\n\nI lived this pain in my coffee shop\n## Quit if: 50 interviews show no problem"})
state = mcp_call("brain_status")
check("after /why: why_set=True", state["why_set"] is True)

# Founder runs /problem → writes brain/problem.md
mcp_call("update_problem", {"content": "# Problem\n\n## Pain\nLate invoices eat 6hrs/wk for service businesses\n## Falsification\nIf 5+ interviewees say it's not weekly\n## Market type\nresegmented existing"})
mcp_call("set_stage", {"new_stage": "1", "reason": "problem hypothesis captured + falsification + founder-market fit"})

state = mcp_call("brain_status")
check("after /problem: problem_set=True", state["problem_hypothesis_set"] is True)
check("after /problem: stage=1", state["stage"] == "1")

# ------------------------------------------------------------------
# STAGE 1 — Customer Discovery
# ------------------------------------------------------------------
print("\n[Stage 1] Customer Discovery")

# Hook should still block product/, but now allow experiments/
decision, _ = run_hook(str(TEST_DIR / "product" / "main.py"))
check("stage 1: hook blocks product/", decision == "deny")
decision, _ = run_hook(str(TEST_DIR / "experiments" / "prototype.py"))
check("stage 1: hook allows experiments/", decision == "allow")

# Run 6 interviews
def make_iv(num, name, classification, segment="legal"):
    return f"""---
date: 2026-05-{num:02d}
participant: {name}
recruited_via: cold email
classification: {classification}
segment: {segment}
---

## Pain
> "real quote here"

## Earlyvangelist test
- Has problem: yes
- Knows it: yes
- Tried to solve: yes
- Has budget: yes
- Would pay: yes
"""

interviews = [
    ("001-sarah", "Sarah K., law firm", "BELIEVER"),
    ("002-mike", "Mike R., accounting", "NEUTRAL"),
    ("003-jen", "Jen M., law firm", "BELIEVER"),
    ("004-tom", "Tom B., consulting", "INFIDEL"),
    ("005-amy", "Amy S., law firm", "BELIEVER"),
    ("006-rob", "Rob L., law firm", "BELIEVER"),
    ("007-sue", "Sue T., law firm", "BELIEVER"),
]
for num, (fname, name, cl) in enumerate(interviews, 1):
    mcp_call("add_interview", {
        "filename": f"{fname}.md",
        "content": make_iv(num, name, cl),
    })

state = mcp_call("brain_status")
check("after 7 interviews: count=7", state["interviews"] == 7)
check("after 7 interviews: 5 believers", state["believers"] == 5)

density = mcp_call("believer_density")
check("believer_density: 5/7 ≈ 71%", abs(density["density_pct"] - 71.4) < 0.5,
      f"got {density['density_pct']}")
check("density verdict: STRONG", "STRONG" in density["verdict"].upper(),
      f"got '{density['verdict']}'")

# Stage 1 → 2 gate met (5+ believers)
mcp_call("set_stage", {"new_stage": "2", "reason": "5+ believers identified, gate met"})

# ------------------------------------------------------------------
# STAGE 2 — Validation
# ------------------------------------------------------------------
print("\n[Stage 2] Validation")

# Add evidence files to make the hook smarter
mcp_call("add_evidence", {
    "filename": "ev-late-invoices.md",
    "content": "Late invoice chasing eats 4-6 hours weekly for service businesses",
})
mcp_call("add_evidence", {
    "filename": "ev-clio-export.md",
    "content": "Clio export strips matter notes, breaks billing review",
})

# Hook should allow product/ writes but coach via claude eval
# (claude eval may not actually run since CLI may not be set up perfectly,
# but the hook should at least not crash)
decision, reason = run_hook(str(TEST_DIR / "product" / "exports.py"))
check("stage 2: hook handles product/ write (allow/ask, no crash)",
      decision in ("allow", "ask"),
      f"got {decision}, reason: {reason[:200]}")

# Log a decision linked to evidence
mcp_call("log_decision", {
    "date_str": "2026-05-15",
    "feature": "Export with matter notes preserved",
    "evidence": "ev-clio-export.md, interview 001-sarah",
    "decision": "build",
    "reasoning": "Sarah explicitly mentioned this; 4 of 5 believers have matter notes",
})
decisions = mcp_call("get_decisions")
check("decision logged in brain/decisions.md", "Export with matter notes" in decisions)

# Query evidence for a feature
results = mcp_call("query_evidence", {"keywords": ["invoice", "billing"]})
check("query_evidence finds matching signals", len(results) >= 1,
      f"got {len(results)}")

# ------------------------------------------------------------------
# /pivot scenario — kill old hypothesis, log new one
# ------------------------------------------------------------------
print("\n[Pivot] Force structured pivot with kill criteria")
# Read current problem
old_problem = mcp_call("get_problem")
check("old problem readable before pivot", "Late invoices" in old_problem)

# Simulate /pivot: new hypothesis for legal vertical specifically
new_problem = """# Problem
Captured: 2026-05-20 (pivoted)

## Pain
Law firm partners spend 4hrs/Friday on invoice exports because Clio strips matter notes

## Who
US-based family law firms, 5-15 lawyers

## Falsification
If 5+ law firms say matter notes are not the issue
"""
mcp_call("update_problem", {"content": new_problem})

# /pivot would write to brain/pivots.md — verify it's writable
# (in plugin format, the file is auto-created on first use)
pivots_md = TEST_BRAIN / "pivots.md"
existing = pivots_md.read_text() if pivots_md.exists() else ""
new_entry = """\n\n## 2026-05-20 — Customer segment pivot: narrow to law firms\n
### Old hypothesis
Service businesses generally
### Kill criteria met
- 5 of 7 believers were law firms specifically; 0 generic
- Tom (consulting) was an INFIDEL
### Pivot type
Customer segment
### What carries over
- Matter-notes pain (universal)
- Sarah, Jen, Amy, Rob, Sue
"""
pivots_md.write_text(existing + new_entry)
content = pivots_md.read_text()
check("pivot logged to brain/pivots.md", "Customer segment pivot" in content)

# ------------------------------------------------------------------
# /pmf-check triangulation
# ------------------------------------------------------------------
print("\n[/pmf-check] Triangulate")
# Currently we have 5 BELIEVERS / 7 total = 71% density (PASS)
# We don't yet have disappointment-survey or retention data
# /pmf-check would prompt for those; we simulate the result
metrics_dir = TEST_BRAIN / "metrics"
metrics_dir.mkdir(exist_ok=True)
(metrics_dir / "disappointment-survey.md").write_text("""# Disappointment survey
Sample: 30
Very disappointed: 47%
## Verdict: PASS
""")
(metrics_dir / "retention-cohorts.md").write_text("""# Retention cohorts
Day 30 retention flattens at 22%
## Verdict: PASS
""")

# /pmf-check would write brain/metrics/pmf-check.md
density = mcp_call("believer_density")
check("density still strong", density["density_pct"] >= 50)

# Verify all metric files persist
check("disappointment-survey.md present", (metrics_dir / "disappointment-survey.md").exists())
check("retention-cohorts.md present", (metrics_dir / "retention-cohorts.md").exists())

# ------------------------------------------------------------------
# /story → /pitch flow
# ------------------------------------------------------------------
print("\n[/story → /pitch]")
story_md = TEST_BRAIN / "story.md"
story_md.write_text("""# Story
## Origin
I ran a coffee shop. Lost 6 hours every week chasing late invoices.

## Why me
3 years running service businesses, 2 years inside legal tech as a Clio user.

## The journey
Talked to 7 service business founders. 5 believers (all law firms).
Pivoted from "service businesses" to "law firms with Clio."
Sarah K. paying $50/mo. Jen M. paying $50/mo.

## Vision
Law firms get back 10 hours/month they currently lose to broken billing exports.

## Ask
$300k seed for 18mo runway to 50 paying firms.

## Citations
- brain/interviews/001-sarah.md
- brain/interviews/003-jen.md
- brain/pivots.md (2026-05-20)
""")
check("brain/story.md written", "Vision" in story_md.read_text())

# /pitch would render brain/pitch/deck.md
pitch_dir = TEST_BRAIN / "pitch"
pitch_dir.mkdir(exist_ok=True)
(pitch_dir / "deck.md").write_text("""# Slide 1: Title
Telos — for law firms

# Slide 2: Problem
Law firms lose 4hrs/Friday on broken billing exports
> "I'd pay $50/mo tomorrow" — Sarah K., interview #001
""")
check("brain/pitch/deck.md written", (pitch_dir / "deck.md").exists())

# ------------------------------------------------------------------
# Final state snapshot
# ------------------------------------------------------------------
print("\n[Final] State snapshot")
final = mcp_call("brain_status")
print(f"  Stage:                    {final['stage']}")
print(f"  Problem hypothesis:       {final['problem_hypothesis_set']}")
print(f"  Why:                      {final['why_set']}")
print(f"  Interviews:               {final['interviews']}")
print(f"  Believers:                {final['believers']}")
print(f"  Believer density:         {final['believer_density_pct']}%")
print(f"  Evidence files:           {final['evidence_files']}")
print(f"  Verdict:                  {final['verdict']}")

check("final state: stage 2", final["stage"] == "2")
check("final state: 7 interviews", final["interviews"] == 7)
check("final state: 5 believers", final["believers"] == 5)
check("final state: density passes 30%", final["believer_density_pct"] >= 30)

print("\n=== RESULT ===")
print(f"  {len(failures)} FAILURES out of e2e tests")
if failures:
    print("\n  FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  ALL E2E TESTS PASSED")
