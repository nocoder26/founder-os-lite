"""End-to-end integration test: spawn the MCP server as a subprocess
and verify the protocol handshake — this is exactly what Claude Code does.

Run from the repo root: python3 tests/test_integration.py
"""
import subprocess
import json
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_CMD = ["python3", str(REPO_ROOT / "plugins" / "telos" / "brain-mcp" / "server.py")]

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} -- {detail}")
        failures.append(label)


print("=== SUBPROCESS HANDSHAKE ===")

env = os.environ.copy()
env["BRAIN_DIR"] = str(REPO_ROOT / "brain")

proc = subprocess.Popen(
    SERVER_CMD,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    text=True,
    bufsize=0,
)


def send(req):
    msg = json.dumps(req) + "\n"
    proc.stdin.write(msg)
    proc.stdin.flush()


def recv():
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)


# 1. initialize
send({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test-harness", "version": "1.0"}
    }
})
resp = recv()
check("initialize returns response", resp is not None)
if resp:
    check("initialize has result", "result" in resp)
    check("server identifies as telos-brain",
          resp.get("result", {}).get("serverInfo", {}).get("name") == "telos-brain")

# 2. notifications/initialized
send({"jsonrpc": "2.0", "method": "notifications/initialized"})

# 3. tools/list
send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
resp = recv()
check("tools/list returns response", resp is not None)
if resp:
    tools = resp.get("result", {}).get("tools", [])
    check("21 tools listed", len(tools) == 21, f"got {len(tools)}")

    expected_tools = {
        "get_stage", "set_stage", "get_problem", "update_problem",
        "get_why", "update_why", "append_journey",
        "list_interviews", "get_interview", "add_interview",
        "list_evidence", "add_evidence", "query_evidence",
        "get_believers_index", "update_believers_index", "believer_density",
        "get_runway", "update_runway",
        "get_decisions", "log_decision",
        "brain_status",
    }
    actual_tools = {t["name"] for t in tools}
    missing = expected_tools - actual_tools
    extra = actual_tools - expected_tools
    check("expected tools all present", not missing, f"missing: {missing}")
    check("no unexpected tools", not extra, f"extra: {extra}")

# 4. tools/call brain_status
send({
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {"name": "brain_status", "arguments": {}}
})
resp = recv()
check("brain_status call returns response", resp is not None)
if resp:
    content = resp.get("result", {}).get("content", [])
    check("brain_status returns content", len(content) > 0)
    if content:
        text = content[0].get("text", "")
        try:
            data = json.loads(text)
            check("brain_status JSON parses", True)
            check("brain_status has 'stage'", "stage" in data)
            check("brain_status has 'verdict'", "verdict" in data)
        except json.JSONDecodeError:
            check("brain_status JSON parses", False, text)

proc.stdin.close()
try:
    proc.wait(timeout=3)
except subprocess.TimeoutExpired:
    proc.kill()

print("\n=== RESULT ===")
if failures:
    print(f"  {len(failures)} FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  ALL INTEGRATION CHECKS PASSED")
