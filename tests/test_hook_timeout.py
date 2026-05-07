"""Verify the hook's timeout protection works cross-platform.

Tests four scenarios:
  [A] No timeout/gtimeout binary, no claude  → graceful 'ask' (no hang)
  [B] Real timeout + hanging claude           → timeout fires at 30s, returns 'ask'
  [C] Fast claude returning GREEN             → silent allow
  [D] Fast claude returning RED               → 'ask' with reason

[B] requires real GNU timeout (or gtimeout) on PATH. On Linux CI it's always
present at /usr/bin/timeout. On macOS install with `brew install coreutils`.

Run from repo root: python3 tests/test_hook_timeout.py
"""
import os
import json
import shutil
import subprocess
import time
import tempfile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / "plugins/telos/hooks/pre-build-coach.sh"

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} -- {detail}")
        failures.append(label)


def find_real_timeout():
    """Find a real GNU timeout binary. Returns path string or None."""
    for cmd in ("timeout", "gtimeout"):
        for prefix in ("/usr/bin", "/opt/homebrew/bin", "/usr/local/bin"):
            p = Path(prefix) / cmd
            if p.exists():
                return str(p)
    return shutil.which("timeout") or shutil.which("gtimeout")


def make_project(stage, evidence=True):
    p = Path(tempfile.mkdtemp(prefix="hook-timeout-test-"))
    (p / "brain/evidence").mkdir(parents=True)
    (p / "brain/believers").mkdir(parents=True)
    (p / "brain/interviews").mkdir(parents=True)
    (p / "product").mkdir()
    (p / "brain/stage.md").write_text(f"# Stage\ncurrent: {stage}\n")
    if evidence:
        (p / "brain/evidence/ev.md").write_text("Late invoice billing matter notes")
    return p


def run_hook(project, env_overrides):
    inp = json.dumps({
        "tool_name": "Write",
        "tool_input": {
            "file_path": str(project / "product" / "main.py"),
            "content": "x = 1",
        },
    })
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project)
    env.update(env_overrides)
    t0 = time.time()
    try:
        r = subprocess.run([str(HOOK)], input=inp, capture_output=True, text=True, env=env, timeout=60)
        elapsed = time.time() - t0
        decision = "?"
        if r.stdout.strip():
            try:
                d = json.loads(r.stdout)
                decision = d.get("hookSpecificOutput", {}).get("permissionDecision", "?")
            except json.JSONDecodeError:
                decision = "parse_error"
        else:
            decision = "allow"
        return elapsed, decision, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return time.time() - t0, "HUNG", "", ""


print("=== HOOK TIMEOUT VERIFICATION ===\n")

# [A] No timeout/claude → graceful ask
print("[A] No timeout binary, no claude → graceful 'ask'")
fake_dir = Path(tempfile.mkdtemp(prefix="bin-A-"))
project = make_project("2")
elapsed, decision, _, _ = run_hook(project, {"PATH": f"{fake_dir}:/usr/bin:/bin"})
print(f"  elapsed: {elapsed:.2f}s, decision: {decision}")
check("[A] returns quickly (<5s)", elapsed < 5.0)
check("[A] returns 'ask' (graceful)", decision == "ask")
shutil.rmtree(fake_dir, ignore_errors=True)
shutil.rmtree(project, ignore_errors=True)

# [B] Real timeout + hanging claude → fires at 30s
print("\n[B] Real timeout + hanging claude → 30s timeout fires")
real_to = find_real_timeout()
if real_to is None:
    print("  SKIP  no GNU timeout/gtimeout on PATH (install with `brew install coreutils` on macOS)")
else:
    print(f"  using: {real_to}")
    fake_dir = Path(tempfile.mkdtemp(prefix="bin-B-"))
    (fake_dir / "claude").write_text("#!/bin/bash\nexec sleep 600\n")
    (fake_dir / "claude").chmod(0o755)
    # Symlink the real timeout binary into our test dir under both names
    shutil.copy(real_to, fake_dir / "timeout")
    shutil.copy(real_to, fake_dir / "gtimeout")

    project = make_project("2")
    elapsed, decision, _, _ = run_hook(project, {"PATH": f"{fake_dir}:/usr/bin:/bin"})
    print(f"  elapsed: {elapsed:.2f}s, decision: {decision}")
    check("[B] timeout fires in 25-40s window", 25 < elapsed < 40, f"elapsed={elapsed:.2f}s")
    check("[B] returns 'ask' (AMBER fallback)", decision == "ask")
    shutil.rmtree(fake_dir, ignore_errors=True)
    shutil.rmtree(project, ignore_errors=True)

# [C] Fast claude returning GREEN → silent allow
print("\n[C] Fast claude returning GREEN → silent allow")
real_to = find_real_timeout()
if real_to is None:
    print("  SKIP  no GNU timeout on PATH")
else:
    fake_dir = Path(tempfile.mkdtemp(prefix="bin-C-"))
    shutil.copy(real_to, fake_dir / "timeout")
    shutil.copy(real_to, fake_dir / "gtimeout")
    (fake_dir / "claude").write_text("""#!/bin/bash
cat > /dev/null
echo "VERDICT: GREEN"
echo "ONELINE: evidence supports this"
""")
    (fake_dir / "claude").chmod(0o755)
    project = make_project("2")
    elapsed, decision, _, _ = run_hook(project, {"PATH": f"{fake_dir}:/usr/bin:/bin"})
    print(f"  elapsed: {elapsed:.2f}s, decision: {decision}")
    check("[C] fast path <5s", elapsed < 5.0)
    check("[C] GREEN → silent allow", decision == "allow")
    shutil.rmtree(fake_dir, ignore_errors=True)
    shutil.rmtree(project, ignore_errors=True)

# [D] Fast claude returning RED → ask with reason
print("\n[D] Fast claude returning RED → 'ask' with reason")
real_to = find_real_timeout()
if real_to is None:
    print("  SKIP  no GNU timeout on PATH")
else:
    fake_dir = Path(tempfile.mkdtemp(prefix="bin-D-"))
    shutil.copy(real_to, fake_dir / "timeout")
    shutil.copy(real_to, fake_dir / "gtimeout")
    (fake_dir / "claude").write_text("""#!/bin/bash
cat > /dev/null
echo "VERDICT: RED"
echo "ONELINE: no evidence supports this"
""")
    (fake_dir / "claude").chmod(0o755)
    project = make_project("2")
    elapsed, decision, out, _ = run_hook(project, {"PATH": f"{fake_dir}:/usr/bin:/bin"})
    print(f"  elapsed: {elapsed:.2f}s, decision: {decision}")
    check("[D] RED → ask", decision == "ask")
    check("[D] reason includes 'no evidence' / 'no matching evidence'",
          "no matching evidence" in out.lower() or "no evidence" in out.lower(),
          f"out: {out[:200]}")
    shutil.rmtree(fake_dir, ignore_errors=True)
    shutil.rmtree(project, ignore_errors=True)

print("\n=== RESULT ===")
print(f"  {len(failures)} FAILURES")
if failures:
    print("\n  FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  HOOK TIMEOUT VERIFIED")
