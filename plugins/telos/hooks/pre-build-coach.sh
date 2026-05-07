#!/bin/bash
#
# pre-build-coach.sh — the "AI says no" enforcement
#
# Runs before Write|Edit. Reads brain/stage.md to determine current stage,
# then either blocks (Discovery → product/), coaches (Validation → check evidence),
# or allows silently.
#
# Hybrid: fast bash checks for stage + file path patterns; only invokes
# Claude evaluator for Stage 2 evidence matching (slow but smart).
#
# Input via stdin: JSON with tool_name, tool_input.file_path, tool_input.content
# Output to stdout: JSON for hookSpecificOutput

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
BRAIN_DIR="$PROJECT_DIR/brain"
STAGE_FILE="$BRAIN_DIR/stage.md"
EVIDENCE_DIR="$BRAIN_DIR/evidence"
BELIEVERS_FILE="$BRAIN_DIR/believers/index.md"

# Plugin-mode safety: if there's no brain/ in the user's current project,
# this hook isn't relevant — exit silently. The plugin may be installed
# globally and firing in a project that isn't a Telos startup.
if [ ! -d "$BRAIN_DIR" ]; then
  exit 0
fi

# Read tool input from stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Helper: emit a hook output JSON and exit
emit_decision() {
  local decision="$1"
  local reason="$2"
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "$decision",
    "permissionDecisionReason": $(echo "$reason" | jq -Rs .)
  }
}
EOF
  exit 0
}

# If no file path, allow (probably not a file edit)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Determine current stage (default 0 if missing)
STAGE="0"
if [ -f "$STAGE_FILE" ]; then
  STAGE=$(grep -E "^current:" "$STAGE_FILE" 2>/dev/null | head -1 | awk '{print $2}' || echo "0")
fi

# Always allow writes to brain/ (state mgmt) and .claude/ (config)
case "$FILE_PATH" in
  *"/brain/"*|*"/.claude/"*)
    exit 0
    ;;
esac

# Stage-based gating
case "$STAGE" in
  "0")
    # Pre-Discovery: only brain/ allowed (already passed above)
    case "$FILE_PATH" in
      *"/experiments/"*|*"/product/"*)
        emit_decision "deny" "Stage 0 (Pre-Discovery). No code yet — not even experiments. You need a problem hypothesis first. Run /problem."
        ;;
    esac
    ;;
  "1")
    # Discovery: experiments/ allowed, product/ blocked
    case "$FILE_PATH" in
      *"/product/"*)
        # Count believers to give specific feedback
        BELIEVER_COUNT=0
        if [ -f "$BELIEVERS_FILE" ]; then
          BELIEVER_COUNT=$(grep -c "BELIEVER" "$BELIEVERS_FILE" 2>/dev/null || echo "0")
        fi
        emit_decision "deny" "Stage 1 (Discovery). product/ is blocked until 5+ believers identified. You have $BELIEVER_COUNT. Options: (a) run /interview to find more, (b) write to experiments/ for a throwaway prototype, (c) /skip-gate with documented justification."
        ;;
    esac
    ;;
  "2")
    # Validation: product/ allowed but coached against evidence
    case "$FILE_PATH" in
      *"/product/"*)
        # Check if there's any evidence to match against
        if [ ! -d "$EVIDENCE_DIR" ] || [ -z "$(ls -A "$EVIDENCE_DIR" 2>/dev/null)" ]; then
          emit_decision "ask" "Stage 2 (Validation), but brain/evidence/ is empty. Building product without logged evidence is back-sliding. Run /interview to populate evidence, or confirm to proceed speculatively."
        fi

        # Stage 2 with evidence: ask Claude to evaluate match.
        # Cross-platform timeout: GNU `timeout` (Linux/CI), `gtimeout` (macOS+coreutils),
        # else degrade gracefully to a manual /build-check prompt.
        TIMEOUT_BIN=""
        if command -v timeout &> /dev/null; then
          TIMEOUT_BIN="timeout 30s"
        elif command -v gtimeout &> /dev/null; then
          TIMEOUT_BIN="gtimeout 30s"
        fi

        if [ -n "$TIMEOUT_BIN" ] && command -v claude &> /dev/null; then
          # Concatenate evidence (capped at 50KB to keep prompt manageable)
          EVIDENCE_CONTENT=$(find "$EVIDENCE_DIR" -name "*.md" -exec cat {} + 2>/dev/null | head -c 50000)
          NEW_CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty' | head -c 5000)

          PROMPT="You are checking if a code change is supported by customer evidence in a founder's brain.

EVIDENCE FROM INTERVIEWS:
---
$EVIDENCE_CONTENT
---

PROPOSED CODE CHANGE (file: $FILE_PATH):
---
$NEW_CONTENT
---

Does at least one evidence entry directly support this code change? Reply in exactly this format:
VERDICT: GREEN | AMBER | RED
ONELINE: <one sentence explaining the verdict, citing the closest evidence entry by name>"

          VERDICT_OUTPUT=$(echo "$PROMPT" | $TIMEOUT_BIN claude -p --max-turns 1 2>/dev/null || echo "VERDICT: AMBER")
          VERDICT=$(echo "$VERDICT_OUTPUT" | grep -E "^VERDICT:" | head -1 | awk '{print $2}' || echo "AMBER")
          ONELINE=$(echo "$VERDICT_OUTPUT" | grep -E "^ONELINE:" | head -1 | sed 's/^ONELINE: //' || echo "evidence check inconclusive")

          case "$VERDICT" in
            "RED")
              emit_decision "ask" "🔴 No matching evidence. $ONELINE. Run /build-check for full options, /interview to gather signal, or confirm to proceed speculatively."
              ;;
            "AMBER")
              emit_decision "ask" "🟡 Related but not direct evidence. $ONELINE. Confirm to proceed, or /build-check for full options."
              ;;
            "GREEN")
              # Allow silently
              exit 0
              ;;
          esac
        else
          # No timeout binary AND/OR no claude CLI — degrade to explicit ask.
          # Avoids both (a) hangs from un-bounded claude calls, and (b) silently
          # skipping evidence checks. macOS users can `brew install coreutils`
          # to get gtimeout if they want the auto-eval path.
          emit_decision "ask" "Stage 2 (Validation): writing to product/. Run /build-check to verify customer evidence supports this change, or confirm to proceed speculatively."
        fi
        ;;
    esac
    ;;
  "3"|"4")
    # Growth and Company Building: less restrictive, just allow
    exit 0
    ;;
esac

# Default: allow
exit 0
