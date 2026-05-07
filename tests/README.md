# Tests

**~265 checks across 8 suites.** All passing.

## Run all

```bash
pip install -r brain-mcp/requirements.txt
python3 tests/test_mcp.py            # 30 MCP unit tests
bash   tests/test_hook.sh            # 12 hook tests
python3 tests/test_skills.py         # 104 skill frontmatter checks (13 skills × 8)
python3 tests/test_integration.py    # 12 MCP protocol handshake tests
python3 tests/test_adversarial.py    # 45 adversarial / security / edge cases
python3 tests/test_e2e.py            # 30 E2E founder-workflow checks
python3 tests/test_hook_timeout.py   # 8 cross-platform hook timeout checks
python3 tests/test_new_skills.py     # 36 design-invariant checks for start, roleplay, gbrain
```

## Hook timeout test note

`test_hook_timeout.py` exercises the hook's protection against hanging
`claude -p` calls. Three of its checks ([B], [C], [D]) require GNU `timeout`
or `gtimeout` on PATH — present at `/usr/bin/timeout` on Linux/CI by default,
needs `brew install coreutils` on macOS for `gtimeout`. If neither is
available, those checks are skipped with a "SKIP" note rather than failing.

## What's covered

- **`test_mcp.py`** — every brain MCP tool exercised: stage transitions, problem/why CRUD, interview management, believer classification + density math, evidence query, decision log, journey log
- **`test_hook.sh`** — `pre-build-coach.sh` at every stage (0–3), with edge cases: missing `stage.md`, `brain/` always-allow
- **`test_skills.py`** — every SKILL.md has valid frontmatter, name matches directory, description ≥ 30 chars, references `brain/`
- **`test_integration.py`** — spawns `brain-mcp/server.py` as a subprocess and runs the actual MCP protocol (initialize → tools/list → tools/call) the same way Claude Code does
- **`test_adversarial.py`** — corrupted brain files, malformed frontmatter, path traversal attempts, unicode, oversized content, empty inputs, edge filenames, hook with bad inputs
- **`test_e2e.py`** — full founder workflow: cold start → `/why` → `/problem` → 7 interviews → believer-density → stage advancement → `/build-check` → `/pivot` → `/pmf-check` → `/story` → `/pitch`
- **`test_new_skills.py`** — structural design invariants for the three skills added after v0 was first drafted: `/telos:start` (concierge bootstraps brain/, chains the right skills, has escape hatch), `/telos:roleplay` (adversarial customer rules, brain/practice/ namespacing, frequency cap, v2 argument-disengage), `/telos:gbrain` (health-check-first, idempotent via hashes, CONFLICT detection, per-file failure isolation, audit trail, telos-managed tag boundary). These tests check what the SKILL.md text MUST contain — they don't run the LLM, they verify the prompt encodes the right invariants.

## What's NOT covered

- LLM (Claude) interpretation of skill prompts — depends on Claude Code runtime
- The hook's `claude -p` evidence-matcher path — requires actual Claude Code CLI; tests strip it from PATH so the bash logic runs in isolation
- Real customer interviews — out of scope for unit tests

## Adding tests when adding skills

If you add a new `/<skill>`:

1. Add to `EXPECTED_SKILLS` in `test_skills.py` (8 frontmatter checks added automatically)
2. Add a workflow step in `test_e2e.py` if it changes brain state
3. Add adversarial cases for any new MCP tools in `test_adversarial.py`
