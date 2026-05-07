"""End-to-end tests for the brain MCP server.

Run from the repo root:
    pip install -r brain-mcp/requirements.txt
    python3 tests/test_mcp.py
"""
import sys
import asyncio
import json
import shutil
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_BRAIN = Path("/tmp/telos-test-brain")

# Set up clean test brain (plugin format: brain/ is per-project, created on demand)
if TEST_BRAIN.exists():
    shutil.rmtree(TEST_BRAIN)
TEST_BRAIN.mkdir(parents=True)
(TEST_BRAIN / "stage.md").write_text("# Stage\ncurrent: 0\n")
(TEST_BRAIN / "interviews").mkdir()
(TEST_BRAIN / "evidence").mkdir()
(TEST_BRAIN / "believers").mkdir()

# Point server at test brain
os.environ["BRAIN_DIR"] = str(TEST_BRAIN)

sys.path.insert(0, str(REPO_ROOT / "plugins" / "telos" / "brain-mcp"))
import server  # noqa: E402


async def call(name, args=None):
    """Call an MCP tool and return parsed result."""
    r = await server.mcp.call_tool(name, args or {})
    if isinstance(r, tuple):
        return r[1]["result"]
    text = r[0].text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text


async def run():
    failures = []

    def check(label, cond, detail=""):
        if cond:
            print(f"  PASS  {label}")
        else:
            print(f"  FAIL  {label} -- {detail}")
            failures.append(label)

    print("=== STAGE & FRESH STATE ===")
    state = await call("brain_status")
    check("fresh stage is 0", state["stage"] == "0", state)
    check("no problem hypothesis", state["problem_hypothesis_set"] is False)
    check("no why set", state["why_set"] is False)
    check("0 interviews", state["interviews"] == 0)

    stage = await call("get_stage")
    check("get_stage returns 0", stage == "0", stage)

    print("\n=== PROBLEM ===")
    msg = await call("update_problem", {"content": "# Problem\nLate invoices eat 6hrs/wk"})
    check("update_problem returns msg", "updated" in msg.lower(), msg)
    p = await call("get_problem")
    check("problem readback", "Late invoices" in p)

    print("\n=== WHY ===")
    await call("update_why", {"content": "# Why\nLived this pain in coffee shop"})
    w = await call("get_why")
    check("why readback", "coffee shop" in w)

    print("\n=== STAGE TRANSITION ===")
    msg = await call("set_stage", {"new_stage": "1", "reason": "hypothesis captured"})
    check("set_stage 0 to 1", "1" in msg)
    s = await call("get_stage")
    check("stage now 1", s == "1", s)
    msg = await call("set_stage", {"new_stage": "9", "reason": "x"})
    check("invalid stage rejected", "Error" in msg, msg)

    print("\n=== INTERVIEWS ===")
    iv1 = "---\ndate: 2026-05-07\nparticipant: Sarah\nclassification: BELIEVER\n---\n## Pain\n> '4 hours every Friday'\n"
    iv2 = "---\ndate: 2026-05-08\nparticipant: Mike\nclassification: NEUTRAL\n---\n## Pain\n> 'sometimes annoying'\n"
    iv3 = "---\ndate: 2026-05-09\nparticipant: Jen\nclassification: BELIEVER\n---\n## Pain\n> 'matter notes stripped'\n"

    await call("add_interview", {"filename": "001-sarah.md", "content": iv1})
    await call("add_interview", {"filename": "002-mike.md", "content": iv2})
    await call("add_interview", {"filename": "003-jen.md", "content": iv3})

    dup = await call("add_interview", {"filename": "001-sarah.md", "content": "x"})
    check("duplicate filename rejected", "already exists" in dup)

    interviews = await call("list_interviews")
    check("3 interviews listed", len(interviews) == 3, len(interviews))
    classifications = [i["classification"] for i in interviews]
    check("classifications parsed", classifications == ["BELIEVER", "NEUTRAL", "BELIEVER"])

    one = await call("get_interview", {"filename": "001-sarah.md"})
    check("get specific interview", "Sarah" in one)
    miss = await call("get_interview", {"filename": "xyz.md"})
    check("missing interview returns error", "not found" in miss.lower())

    print("\n=== BELIEVERS ===")
    density = await call("believer_density")
    check("density: 2 believers", density["believer_count"] == 2)
    check("density: 67%", abs(density["density_pct"] - 66.7) < 0.1)
    check("density: 1 neutral", density["neutral_count"] == 1)

    print("\n=== EVIDENCE ===")
    await call("add_evidence", {"filename": "ev1.md", "content": "Late invoice chasing eats hours weekly"})
    await call("add_evidence", {"filename": "ev2.md", "content": "Matter notes get stripped on export"})

    files = await call("list_evidence")
    check("2 evidence files", len(files) == 2)

    matches = await call("query_evidence", {"keywords": ["invoice"]})
    check("query 'invoice' finds 1", len(matches) == 1)
    matches = await call("query_evidence", {"keywords": ["matter", "notes"]})
    check("query 'matter notes' finds 1", len(matches) == 1)
    matches = await call("query_evidence", {"keywords": ["nonexistent"]})
    check("query nonexistent finds 0", len(matches) == 0)

    print("\n=== DECISIONS ===")
    msg = await call("log_decision", {
        "date_str": "2026-05-07", "feature": "Export to CSV",
        "evidence": "001-sarah", "decision": "build", "reasoning": "verbatim quote"
    })
    check("decision logged", "logged" in msg.lower())
    decisions = await call("get_decisions")
    check("decision in log", "Export to CSV" in decisions)

    print("\n=== JOURNEY ===")
    await call("append_journey", {
        "date_str": "2026-05-07", "context": "first hard moment",
        "trigger": "essay flopped", "response": "kept going"
    })
    j = (TEST_BRAIN / "journey.md").read_text()
    check("journey created", "first hard moment" in j)

    print("\n=== FINAL STATUS ===")
    final = await call("brain_status")
    check("final stage 1", final["stage"] == "1")
    check("final 3 interviews", final["interviews"] == 3)
    check("final 2 believers", final["believers"] == 2)
    check("final 2 evidence", final["evidence_files"] == 2)

    print("\n=== RESULT ===")
    if failures:
        print(f"  {len(failures)} FAILURES:")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)
    else:
        print("  ALL TESTS PASSED")


asyncio.run(run())
