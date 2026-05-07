#!/bin/bash
# Test pre-build-coach.sh at each stage with various file paths.
# Run from the repo root: bash tests/test_hook.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$REPO_ROOT/plugins/telos/hooks/pre-build-coach.sh"
TEST_DIR="/tmp/telos-hook-test"
PASS=0
FAIL=0
FAILURES=()

setup_brain() {
    local stage=$1
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR/brain/believers" "$TEST_DIR/brain/evidence" "$TEST_DIR/brain/interviews"
    mkdir -p "$TEST_DIR/product" "$TEST_DIR/experiments"
    cat > "$TEST_DIR/brain/stage.md" <<EOF
# Stage
current: $stage
EOF
}

run_hook() {
    local file_path=$1
    local content=${2:-"some content"}
    local input
    input=$(cat <<EOF
{"tool_name": "Write", "tool_input": {"file_path": "$file_path", "content": "$content"}}
EOF
)
    CLAUDE_PROJECT_DIR="$TEST_DIR" echo "$input" | CLAUDE_PROJECT_DIR="$TEST_DIR" "$HOOK"
}

check() {
    local label=$1
    local expected=$2
    local output=$3
    if [ -z "$output" ]; then
        actual="allow"
    else
        actual=$(echo "$output" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('hookSpecificOutput',{}).get('permissionDecision','allow'))" 2>/dev/null || echo "parse_error")
    fi

    if [ "$actual" == "$expected" ]; then
        echo "  PASS  $label  (got: $actual)"
        PASS=$((PASS+1))
    else
        echo "  FAIL  $label  expected=$expected got=$actual"
        FAILURES+=("$label")
        FAIL=$((FAIL+1))
    fi
}

echo "=== STAGE 0: only brain/ allowed ==="
setup_brain 0
out=$(run_hook "$TEST_DIR/brain/notes.md")
check "stage 0: brain/ allow" "allow" "$out"
out=$(run_hook "$TEST_DIR/product/main.py")
check "stage 0: product/ deny" "deny" "$out"
out=$(run_hook "$TEST_DIR/experiments/test.py")
check "stage 0: experiments/ deny" "deny" "$out"

echo ""
echo "=== STAGE 1: experiments/ allowed, product/ blocked ==="
setup_brain 1
out=$(run_hook "$TEST_DIR/brain/notes.md")
check "stage 1: brain/ allow" "allow" "$out"
out=$(run_hook "$TEST_DIR/experiments/test.py")
check "stage 1: experiments/ allow" "allow" "$out"
out=$(run_hook "$TEST_DIR/product/main.py")
check "stage 1: product/ deny" "deny" "$out"

echo ""
echo "=== STAGE 2: product/ allowed but coached ==="
setup_brain 2
out=$(run_hook "$TEST_DIR/brain/notes.md")
check "stage 2: brain/ allow" "allow" "$out"
out=$(run_hook "$TEST_DIR/experiments/test.py")
check "stage 2: experiments/ allow" "allow" "$out"
out=$(run_hook "$TEST_DIR/product/main.py")
check "stage 2: product/ no evidence => ask" "ask" "$out"

echo ""
echo "=== STAGE 3: less restrictive ==="
setup_brain 3
out=$(run_hook "$TEST_DIR/product/main.py")
check "stage 3: product/ allow" "allow" "$out"

echo ""
echo "=== EDGE CASES ==="
setup_brain 0
out=$(run_hook "$TEST_DIR/.claude/settings.json")
check "any stage: .claude/ allow" "allow" "$out"
rm -f "$TEST_DIR/brain/stage.md"
out=$(run_hook "$TEST_DIR/product/main.py")
check "missing stage.md defaults to 0 (deny)" "deny" "$out"

echo ""
echo "=== RESULT ==="
echo "  $PASS passed, $FAIL failed"
if [ $FAIL -gt 0 ]; then
    echo "  Failures:"
    for f in "${FAILURES[@]}"; do
        echo "    - $f"
    done
    exit 1
fi
