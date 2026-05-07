"""Design-invariant tests for /telos:start, /telos:roleplay, /telos:gbrain.

These tests check structural properties of the SKILL.md files — not LLM
interpretation, but the things the skill prompt MUST contain for the
skill to work as designed:

- start: must auto-bootstrap brain/ skeleton (mkdir command in prompt)
- roleplay: must enforce brain/practice/ namespacing (never brain/interviews/)
- roleplay: must include the adversarial customer prompt template
- roleplay: must declare the pre-flight refusal gates
- roleplay: must declare the frequency cap (anti-substitute)
- roleplay: must include the argument-disengage rules (v2 patch)
- gbrain: must do health check before any other gbrain MCP call
- gbrain: must declare the resilience invariants table
- gbrain: must declare 'CONFLICT' detection
- gbrain: must declare hash-based idempotency

Run from repo root: python3 tests/test_new_skills.py
"""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "plugins" / "telos" / "skills"

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        msg = f"  FAIL  {label}"
        if detail:
            msg += f" -- {detail}"
        print(msg)
        failures.append(label)


def read_skill(name):
    path = SKILLS / name / "SKILL.md"
    if not path.exists():
        check(f"{name}/SKILL.md exists", False, f"missing at {path}")
        return None
    return path.read_text()


# =====================================================================
print("=== /telos:start — concierge invariants ===")
start = read_skill("start")
if start:
    check("start: auto-bootstraps brain/ via mkdir",
          "mkdir -p brain/" in start,
          "must contain 'mkdir -p brain/' in the bootstrap step")
    check("start: creates brain/interviews/ subfolder",
          "brain/interviews" in start)
    check("start: chains to /telos:why",
          "/telos:why" in start,
          "concierge must run /why")
    check("start: chains to /telos:problem",
          "/telos:problem" in start,
          "concierge must run /problem")
    check("start: chains to /telos:interview",
          "/telos:interview" in start,
          "concierge must run /interview")
    check("start: has Mode B for returning founders",
          "Mode B" in start,
          "must handle existing brain/ case")
    check("start: has escape hatch for users who know what they want",
          "I already know" in start,
          "must offer a drop-out for non-onboarding users")


# =====================================================================
print("\n=== /telos:roleplay — adversarial customer invariants ===")
rp = read_skill("roleplay")
if rp:
    # Pre-flight gates
    check("roleplay: refuses with 0 real interviews",
          "0 entries" in rp or "Pre-flight gate 2" in rp or "0 real interview" in rp.lower() or "never talked to a real human" in rp,
          "must have anti-substitute gate when no real interviews exist")
    check("roleplay: declares frequency cap (>2 in 7 days)",
          ">2 roleplays" in rp or "more than 2" in rp.lower() or "practice frequency" in rp.lower(),
          "must enforce a cap that prevents practice-as-substitute")

    # Adversarial customer rules
    check("roleplay: customer has tried alternatives",
          "tried 3" in rp or "alternatives" in rp,
          "customer prompt must declare prior-failed-alternatives behavior")
    check("roleplay: customer protects budget",
          "budget" in rp.lower() and "protective" in rp.lower(),
          "customer prompt must establish budget protection")
    check("roleplay: customer punishes vague language",
          "vague" in rp.lower() or "specifically" in rp,
          "customer prompt must reject vague claims")
    check("roleplay: customer asks founder questions back",
          "questions back" in rp or "asking me this" in rp.lower(),
          "customer prompt must reverse questions to surface founder reasoning")

    # v2 patches — argument handling
    check("roleplay v2: customer disengages on second argument",
          "argues with your pushback a SECOND time" in rp or
          "argues with your pushback a second time" in rp.lower() or
          "second time in the same session, disengage" in rp.lower(),
          "must auto-disengage on repeated arguing")
    check("roleplay v2: meta-interrupt on first argument",
          "ROLEPLAY PAUSED" in rp,
          "must have Telos-side meta-pause when arguing detected")
    check("roleplay v2: critique fronts argument moments",
          "Argument moments" in rp,
          "critique structure must surface argument moments as headline")

    # Namespacing — the most important structural guarantee
    check("roleplay: writes to brain/practice/ (not interviews/)",
          "brain/practice/" in rp,
          "outputs MUST go to brain/practice/")
    check("roleplay: contains explicit warning about not writing to interviews/",
          "never `interviews/`" in rp or
          "never `brain/interviews/`" in rp or
          "never brain/interviews" in rp.lower(),
          "must explicitly forbid writing to brain/interviews/")
    check("roleplay: practice files carry exclusion header",
          "TELOS-PRACTICE-SESSION" in rp,
          "must use the exclusion header so other skills ignore practice files")

    # Tone of critique
    check("roleplay: critique is default-pessimistic",
          "default-pessimistic" in rp.lower() or "Lead with what was weak" in rp,
          "critique tone rules must enforce pessimism-first")
    check("roleplay: refuses to congratulate",
          "Refuse to congratulate" in rp or "refuse to congratulate" in rp.lower(),
          "critique must not validate even good sessions")


# =====================================================================
print("\n=== /telos:gbrain — bridge resilience invariants ===")
gb = read_skill("gbrain")
if gb:
    # The 15 resilience invariants the SKILL.md declares
    check("gbrain: hard-refuses if gbrain MCP not detected",
          "mcp__brain__get_health" in gb and "Refuse" in gb,
          "must check health before any other gbrain operation")
    check("gbrain: declares Telos works without gbrain",
          "Telos works perfectly without" in gb or
          "Telos works fine without" in gb,
          "must establish opt-in / non-dependency")
    check("gbrain: idempotent via hash comparison",
          "SHA-256" in gb or "source_hash" in gb,
          "re-runs must be no-ops via content hashing")
    check("gbrain: detects CONFLICT (gbrain content edited outside Telos)",
          "CONFLICT" in gb,
          "must surface conflicts instead of silent overwrites")
    check("gbrain: per-file failure isolation",
          "Continue with the next file" in gb or
          "continue with other items" in gb or
          "must not abort the whole batch" in gb,
          "single failed sync must not abort batch")
    check("gbrain: writes audit trail",
          "gbrain-log.md" in gb,
          "must log every sync action to brain/integrations/")
    check("gbrain: reverse-links via comment in source file",
          "<!-- gbrain:" in gb,
          "must write gbrain slug back to source markdown")
    check("gbrain: requires explicit setup before sync",
          "setup" in gb and ("refuse all sync operations until setup completes" in gb.lower() or
                              "Refuse all sync operations until setup completes" in gb),
          "must require explicit setup mode")
    check("gbrain: refuses to claim non-Telos pages",
          "telos-managed" in gb,
          "must use telos-managed tag and refuse to overwrite non-tagged pages")
    check("gbrain: includes resilience checklist table",
          "Resilience checklist" in gb or "resilience invariants" in gb.lower(),
          "must document the resilience invariants explicitly")
    check("gbrain: explicit 'does NOT do' boundaries",
          "does NOT" in gb or "explicitly does NOT" in gb,
          "must declare scope boundaries")
    check("gbrain: credits gbrain (Garry Tan)",
          "garrytan/gbrain" in gb or "Garry Tan" in gb,
          "must credit upstream tool")
    check("gbrain: does NOT contain stale Gary Tran / gtanner attribution",
          "Gary Tran" not in gb and "gtanner/gbrain" not in gb,
          "old wrong attribution must be fully removed")


# =====================================================================
# Cross-skill structural checks: practice files must NOT be in
# interviews/, gbrain.yaml integration path is correct, etc.
print("\n=== Cross-skill structural checks ===")

# No skill should pollute brain/interviews/ with practice content
for s in ["roleplay"]:
    body = read_skill(s)
    if body:
        # The text "brain/interviews/" should appear only in pre-flight context,
        # NEVER as the output destination for the skill
        # Heuristic: "writes to brain/interviews/" or "outputs to brain/interviews/"
        # should NOT appear
        bad_phrases = [
            "writes to brain/interviews/",
            "outputs to brain/interviews/",
            "saves to brain/interviews/",
            "Write to brain/interviews/",
        ]
        for phrase in bad_phrases:
            check(f"{s}: does NOT write to brain/interviews/ ('{phrase}')",
                  phrase not in body,
                  f"would corrupt real-interview namespace")


# =====================================================================
print("\n=== RESULT ===")
if failures:
    print(f"  {len(failures)} FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  ALL DESIGN-INVARIANT CHECKS PASSED")
