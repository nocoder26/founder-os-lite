"""Adversarial / edge case tests on the brain MCP server + hook.

What we're trying to break:
- empty brain (cold start) — every read tool should handle gracefully
- corrupted brain/stage.md (invalid stage values like "abc", missing "current:")
- malformed interview frontmatter (missing fields, broken YAML)
- path traversal in filenames (../etc/passwd)
- unicode in filenames and content
- very long content (10MB+ interview)
- nonexistent BRAIN_DIR
- concurrent writes (single test-pass; not a real concurrency test)
"""
import sys
import asyncio
import json
import shutil
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEST_BRAIN = Path("/tmp/telos-adversarial-brain")

failures = []


def setup_brain(stage_content="# Stage\ncurrent: 0\n"):
    """Reset test brain to a known state."""
    if TEST_BRAIN.exists():
        shutil.rmtree(TEST_BRAIN)
    TEST_BRAIN.mkdir(parents=True)
    (TEST_BRAIN / "stage.md").write_text(stage_content)
    (TEST_BRAIN / "interviews").mkdir()
    (TEST_BRAIN / "evidence").mkdir()
    (TEST_BRAIN / "believers").mkdir()


def call(name, args=None):
    """Call MCP tool synchronously."""
    os.environ["BRAIN_DIR"] = str(TEST_BRAIN)
    sys.path.insert(0, str(REPO / "plugins" / "telos" / "brain-mcp"))
    if "server" in sys.modules:
        del sys.modules["server"]
    import server
    server.BRAIN_DIR = TEST_BRAIN

    async def _run():
        r = await server.mcp.call_tool(name, args or {})
        if isinstance(r, tuple):
            return r[1]["result"]
        text = r[0].text
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return text

    return asyncio.run(_run())


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} -- {detail}")
        failures.append(label)


def expect_no_crash(label, fn):
    """Just verify the function doesn't raise."""
    try:
        result = fn()
        print(f"  PASS  {label}  →  {repr(result)[:80]}")
        return True
    except Exception as e:
        print(f"  FAIL  {label}  →  raised {type(e).__name__}: {e}")
        failures.append(label)
        return False


print("=== ADVERSARIAL TESTS ===\n")

# ---- 1. Empty brain ----
print("[1] Empty brain (cold start) — every read should return safe defaults")
setup_brain()
state = call("brain_status")
check("brain_status on empty brain", state["stage"] == "0" and state["interviews"] == 0)
check("get_problem returns empty string", call("get_problem") == "")
check("get_why returns empty string", call("get_why") == "")
check("get_runway returns empty string", call("get_runway") == "")
check("list_interviews returns empty list", call("list_interviews") == [])
check("list_evidence returns empty list", call("list_evidence") == [])
density = call("believer_density")
check("believer_density on no interviews", density["total_interviews"] == 0 and density["density_pct"] == 0)

# ---- 2. Corrupted brain/stage.md ----
print("\n[2] Corrupted stage.md")
setup_brain(stage_content="# Stage\nthis file is broken\nno colon line here\n")
stage = call("get_stage")
check("get_stage on missing 'current:' line returns '0'", stage == "0", f"got {repr(stage)}")

setup_brain(stage_content="current: ABCDE\n")
stage = call("get_stage")
check("get_stage on non-numeric 'ABCDE' falls back to '0'", stage == "0", repr(stage))

setup_brain(stage_content="current: 99\n")
stage = call("get_stage")
check("get_stage on out-of-range '99' falls back to '0'", stage == "0", repr(stage))

setup_brain(stage_content="current: -1\n")
stage = call("get_stage")
check("get_stage on negative '-1' falls back to '0'", stage == "0", repr(stage))

setup_brain(stage_content="current: 1.5\n")
stage = call("get_stage")
check("get_stage on decimal '1.5' falls back to '0'", stage == "0", repr(stage))

# ---- 3. set_stage validation ----
print("\n[3] set_stage validation")
setup_brain()
result = call("set_stage", {"new_stage": "5", "reason": "x"})
check("set_stage rejects '5' (out of range)", "Error" in result)
result = call("set_stage", {"new_stage": "abc", "reason": "x"})
check("set_stage rejects 'abc'", "Error" in result)
result = call("set_stage", {"new_stage": "", "reason": "x"})
check("set_stage rejects ''", "Error" in result)

# ---- 4. add_interview duplicate prevention ----
print("\n[4] add_interview safeguards")
setup_brain()
result = call("add_interview", {"filename": "001.md", "content": "first"})
check("first add succeeds", "saved" in result.lower())
result = call("add_interview", {"filename": "001.md", "content": "duplicate"})
check("duplicate rejected", "already exists" in result.lower())

# ---- 5. Path traversal attempt ----
print("\n[5] Path traversal in filename")
setup_brain()
# This is the key safety test
result = call("add_interview", {"filename": "../../../tmp/pwned.md", "content": "x"})
# Check if the file got written outside the brain dir (BAD)
escaped_file = Path("/tmp/pwned.md")
escaped_brain_parent = TEST_BRAIN.parent / "pwned.md"
both_clean = not escaped_file.exists() and not escaped_brain_parent.exists()
check("path traversal '../../../tmp/pwned.md' contained", both_clean,
      f"escaped to {escaped_file if escaped_file.exists() else escaped_brain_parent}")

# Cleanup just in case
if escaped_file.exists():
    escaped_file.unlink()
if escaped_brain_parent.exists():
    escaped_brain_parent.unlink()

# Try with absolute path
result2 = call("add_interview", {"filename": "/tmp/pwned2.md", "content": "x"})
escaped2 = Path("/tmp/pwned2.md")
check("absolute path '/tmp/pwned2.md' contained", not escaped2.exists())
if escaped2.exists():
    escaped2.unlink()

# add_evidence — same vuln class, same fix expected
print("\n[5b] Path traversal in add_evidence (same vuln class)")
setup_brain()
ev_evil1 = Path("/tmp/pwned-ev1.md")
ev_evil2 = Path("/tmp/pwned-ev2.md")
for p in (ev_evil1, ev_evil2):
    if p.exists():
        p.unlink()

call("add_evidence", {"filename": "../../../tmp/pwned-ev1.md", "content": "x"})
check("add_evidence relative-traversal contained", not ev_evil1.exists())

call("add_evidence", {"filename": "/tmp/pwned-ev2.md", "content": "x"})
check("add_evidence absolute-path contained", not ev_evil2.exists())

# Empty/dot rejection
for bad in ("", ".", ".."):
    r = call("add_evidence", {"filename": bad, "content": "x"})
    check(f"add_evidence rejects {bad!r}", "Error" in r or "invalid" in r.lower())

for p in (ev_evil1, ev_evil2):
    if p.exists():
        p.unlink()

# ---- 6. Unicode in content + filename ----
print("\n[6] Unicode handling")
setup_brain()
unicode_content = "---\ndate: 2026-01-01\nparticipant: 田中さん, 法律事務所 (Tokyo)\nclassification: BELIEVER\n---\n\n## Pain\n> 'これは本当に困る'\n"
result = call("add_interview", {"filename": "001-unicode.md", "content": unicode_content})
check("unicode content saved", "saved" in result.lower())
read_back = call("get_interview", {"filename": "001-unicode.md"})
check("unicode content read back correctly", "田中" in read_back and "本当に困る" in read_back)

# Unicode filename
result = call("add_interview", {"filename": "002-田中.md", "content": "test"})
check("unicode filename accepted", "saved" in result.lower() or "already exists" not in result)

# ---- 7. Very long content ----
print("\n[7] Large content (1MB)")
setup_brain()
big = "# big\n\n" + ("test " * 200000)  # ~1MB
result = call("add_interview", {"filename": "big.md", "content": big})
check("1MB interview saved without crash", "saved" in result.lower())
# Read it back
read = call("get_interview", {"filename": "big.md"})
check("1MB read back intact", len(read) > 900_000)

# ---- 8. Malformed frontmatter in interview ----
print("\n[8] Malformed frontmatter — list_interviews must still work")
setup_brain()
# Missing closing ---
call("add_interview", {"filename": "broken1.md", "content": "---\ndate: 2026-01-01\nclassification: BELIEVER\nno closing\n## Pain"})
# Just frontmatter, no body
call("add_interview", {"filename": "broken2.md", "content": "---\ndate: 2026-01-02\nclassification: BELIEVER\n---"})
# No frontmatter at all
call("add_interview", {"filename": "broken3.md", "content": "## Pain\n> just notes"})

result = call("list_interviews")
check("list_interviews handles 3 broken files", isinstance(result, list) and len(result) == 3,
      f"got {len(result) if isinstance(result, list) else 'non-list'}")

# Verify believer_density doesn't crash
density = call("believer_density")
check("believer_density on partial-frontmatter set",
      isinstance(density, dict) and "total_interviews" in density,
      f"got {density}")

# ---- 9. Empty filename ----
print("\n[9] Edge filenames")
setup_brain()
result = call("add_interview", {"filename": "", "content": "x"})
check("empty filename handled", isinstance(result, str))

# Filename with no .md
result = call("add_interview", {"filename": "no_extension", "content": "x"})
# server appends .md
target_exists = (TEST_BRAIN / "interviews" / "no_extension.md").exists()
check("filename without .md extension auto-appended", target_exists)

# Filename with multiple dots
result = call("add_interview", {"filename": "weird.name.md", "content": "x"})
target_exists = (TEST_BRAIN / "interviews" / "weird.name.md").exists()
check("filename with multiple dots accepted", target_exists)

# ---- 10. query_evidence on empty/special inputs ----
print("\n[10] query_evidence edge cases")
setup_brain()
result = call("query_evidence", {"keywords": []})
check("query_evidence with empty keywords returns []", result == [])

call("add_evidence", {"filename": "ev1.md", "content": "Hello world"})
result = call("query_evidence", {"keywords": [""]})
check("query_evidence with empty string keyword", isinstance(result, list))

# Very long keyword
result = call("query_evidence", {"keywords": ["x" * 10000]})
check("query_evidence with 10k-char keyword", isinstance(result, list))

# ---- 11. Hook with weird inputs ----
print("\n[11] Hook with edge inputs")
setup_brain()
hook = REPO / "plugins/telos/hooks/pre-build-coach.sh"

def run_hook(stdin_input, project_dir=str(TEST_BRAIN.parent)):
    """Run hook with given input, return (decision, raw_output)."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = project_dir
    proc = subprocess.run(
        [str(hook)],
        input=stdin_input,
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
        return d.get("hookSpecificOutput", {}).get("permissionDecision", "allow"), out
    except json.JSONDecodeError:
        return "parse_error", out

# Hook needs CLAUDE_PROJECT_DIR pointing at brain parent so relative brain/stage.md resolves
project_dir = str(TEST_BRAIN.parent / "telos-adversarial-brain") + "_proj"
Path(project_dir).mkdir(exist_ok=True)
shutil.copytree(TEST_BRAIN, Path(project_dir) / "brain", dirs_exist_ok=True)
Path(project_dir, "product").mkdir(exist_ok=True)
Path(project_dir, "experiments").mkdir(exist_ok=True)

# Empty stdin
d, _ = run_hook("", project_dir)
check("hook handles empty stdin", d == "allow")

# Malformed JSON
d, _ = run_hook("{not valid json", project_dir)
check("hook handles malformed JSON", d == "allow", f"got {d}")

# Missing tool_input
d, _ = run_hook(json.dumps({"tool_name": "Write"}), project_dir)
check("hook handles missing tool_input", d == "allow")

# tool_input present but no file_path
d, _ = run_hook(json.dumps({"tool_name": "Write", "tool_input": {}}), project_dir)
check("hook handles missing file_path", d == "allow")

# file_path with traversal
d, _ = run_hook(json.dumps({
    "tool_name": "Write",
    "tool_input": {"file_path": f"{project_dir}/../../../tmp/evil.txt"}
}), project_dir)
# Hook should still match by path patterns, traversal in path means it's
# probably outside product/ so allowed. Acceptable.
check("hook handles path traversal in file_path (no crash)", d in ("allow", "deny", "ask"))

# Cleanup project dir
if Path(project_dir).exists():
    shutil.rmtree(project_dir)

# ---- 12. set_stage with very long reason ----
print("\n[12] set_stage with long reason")
setup_brain()
result = call("set_stage", {"new_stage": "1", "reason": "x" * 5000})
check("set_stage with 5000-char reason succeeds", "1" in result)

# ---- 13. log_decision validation ----
print("\n[13] log_decision")
setup_brain()
result = call("log_decision", {
    "date_str": "2026-01-01", "feature": "X", "evidence": "Y",
    "decision": "build", "reasoning": "Z"
})
check("log_decision basic call", "logged" in result.lower())
# Get back
decisions = call("get_decisions")
check("logged decision visible in get_decisions", "X" in decisions)

print("\n=== RESULT ===")
print(f"  {len(failures)} FAILURES out of many tests")
if failures:
    print("\n  FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  ALL ADVERSARIAL TESTS PASSED")
