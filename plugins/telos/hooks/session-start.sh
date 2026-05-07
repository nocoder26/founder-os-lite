#!/bin/bash
#
# session-start.sh — opt-in pitch + state-aware orientation
#
# Behavior matrix:
#   TELOS_DISABLE_PITCH=1                           → silent always
#   System path (HOME root, /tmp, /usr, etc.)       → silent
#   brain/ exists                                   → state-aware orientation
#   Path in decided.txt                             → silent (already answered)
#   Existing project (package.json, .git, etc.)     → silent (heuristic; override with TELOS_PITCH_ALWAYS=1)
#   Fresh dir, undecided                            → ONE-LINE pitch via additionalContext
#
# Claude reads additionalContext and shapes its first message accordingly.
# When the founder answers, Claude writes their decision to decided.txt
# so future sessions in that path stay silent.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# 1. Global opt-out
if [ "${TELOS_DISABLE_PITCH:-}" = "1" ]; then
  exit 0
fi

# 2. Skip system paths (don't pollute non-project contexts)
case "$PROJECT_DIR" in
  "$HOME"|/tmp*|/var*|/usr*|/etc*|/opt*|/private/*)
    exit 0
    ;;
esac
case "$PROJECT_DIR" in
  "$HOME/Library"*|"$HOME/.claude"*|"$HOME/.config"*|"$HOME/.cache"*)
    exit 0
    ;;
esac

# 3. State directory
STATE_DIR="$HOME/.claude/plugins/telos"
DECIDED_FILE="$STATE_DIR/decided.txt"
mkdir -p "$STATE_DIR"
touch "$DECIDED_FILE"

BRAIN="$PROJECT_DIR/brain"

# 4. brain/ exists → state-aware orientation (engaged founder, returning)
if [ -d "$BRAIN" ]; then
  STAGE="0"
  [ -f "$BRAIN/stage.md" ] && STAGE=$(grep "^current:" "$BRAIN/stage.md" 2>/dev/null | head -1 | awk '{print $2}' || echo "0")

  WHY_SET="no"
  [ -f "$BRAIN/why.md" ] && [ -s "$BRAIN/why.md" ] && ! grep -q "(empty" "$BRAIN/why.md" 2>/dev/null && WHY_SET="yes"

  PROBLEM_SET="no"
  [ -f "$BRAIN/problem.md" ] && [ -s "$BRAIN/problem.md" ] && ! grep -q "(empty" "$BRAIN/problem.md" 2>/dev/null && PROBLEM_SET="yes"

  INTERVIEW_COUNT=0
  [ -d "$BRAIN/interviews" ] && INTERVIEW_COUNT=$(find "$BRAIN/interviews" -name "*.md" -not -name ".gitkeep" 2>/dev/null | wc -l | tr -d ' ')

  BELIEVER_COUNT=0
  [ -f "$BRAIN/believers/index.md" ] && BELIEVER_COUNT=$(grep -ci "BELIEVER" "$BRAIN/believers/index.md" 2>/dev/null || echo "0")

  EVIDENCE_COUNT=0
  [ -d "$BRAIN/evidence" ] && EVIDENCE_COUNT=$(find "$BRAIN/evidence" -name "*.md" -not -name ".gitkeep" 2>/dev/null | wc -l | tr -d ' ')

  # Recommend next action
  if [ "$WHY_SET" = "no" ]; then
    NEXT="/telos:start — concierge walkthrough (10 min, produces a real artifact)"
  elif [ "$PROBLEM_SET" = "no" ]; then
    NEXT="/telos:problem — capture your hypothesis"
  elif [ "$STAGE" = "1" ] && [ "$INTERVIEW_COUNT" -lt 5 ]; then
    NEXT="/telos:interview ($INTERVIEW_COUNT done, need 5+ believers to advance)"
  elif [ "$STAGE" = "1" ] && [ "$BELIEVER_COUNT" -lt 5 ]; then
    NEXT="/telos:believers — classify the $INTERVIEW_COUNT interviews; have $BELIEVER_COUNT believer(s)"
  elif [ "$STAGE" = "2" ]; then
    NEXT="/telos:build-check before any product/ change, or /telos:pmf-check"
  elif [ "$STAGE" = "3" ]; then
    NEXT="/telos:default-alive (re-check runway) or /telos:disrupt-self"
  else
    NEXT="continue your validation flow"
  fi

  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Telos project. Stage $STAGE · why=$WHY_SET · problem=$PROBLEM_SET · ${INTERVIEW_COUNT} interview(s) · ${BELIEVER_COUNT} believer(s) · ${EVIDENCE_COUNT} evidence file(s).\n\nRecommended next: $NEXT.\n\nGreet the founder briefly, surface where they are, recommend the next action. If they want something else, follow them — but flag if it skips an unfilled gate."
  }
}
EOF
  exit 0
fi

# 5. Already declined → silent
if grep -Fxq "$PROJECT_DIR" "$DECIDED_FILE" 2>/dev/null; then
  exit 0
fi

# 6. Heuristic: existing project signals (package.json / .git / etc.) → silent
# Override with TELOS_PITCH_ALWAYS=1 if the founder wants to bootstrap an existing repo.
if [ "${TELOS_PITCH_ALWAYS:-}" != "1" ]; then
  for marker in package.json Cargo.toml requirements.txt Gemfile pyproject.toml go.mod composer.json .git; do
    if [ -e "$PROJECT_DIR/$marker" ]; then
      exit 0
    fi
  done
fi

# 7. Fresh, undecided → one-line pitch
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Telos is loaded for this fresh project (no brain/ yet, no existing decision).\n\nIn your VERY FIRST message to the founder, do EXACTLY this — no more, no less. Output the concierge welcome verbatim, then wait:\n\n  Say: 'I'm Telos. I'll spend 10 minutes asking three questions, and you'll walk out with a real customer-interview script and a hypothesis you can kill. Sound good? (yes / I already know what I want / what is this?)'\n\nThen WAIT for their response. Four cases:\n\n  YES / sounds good / sure / start / continue: immediately run the /telos:start skill from Step 1 onward (skip the welcome since you already said it). Auto-create the brain/ skeleton via Bash, then proceed through /telos:why → /telos:problem → /telos:interview with one-line context before each.\n\n  'I already know what I want' / 'I'll do it myself' / 'just /why': drop out gracefully. Reply: 'Cool — run /telos:why, /telos:problem, or /telos:interview directly when you are ready.' Then silently run this bash to record the decision so we never re-pitch:\n    echo \"$PROJECT_DIR\" >> ~/.claude/plugins/telos/decided.txt\n  Continue as normal Claude session.\n\n  'What is this?' / 'tell me more': one paragraph: 'Telos is a discipline layer for Claude Code. It refuses to let you write product code until you have validated the problem with real customers. The brain/ folder we will build is your record of every interview, decision, and pivot. By the time you raise a round, it is your data room.' Then re-ask the welcome question.\n\n  NO / skip / not now / change subject / ask about something else: silently record the decision (bash above), continue as normal Claude Code session, NEVER bring up Telos again unless they explicitly invoke a /telos:* skill.\n\nDo NOT pitch twice. Do NOT keep nudging. Do NOT volunteer telos skills unless they explicitly ask."
  }
}
EOF
