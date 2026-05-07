"""Validate all SKILL.md files have proper frontmatter.

Run from the repo root: python3 tests/test_skills.py
"""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "plugins" / "telos" / "skills"
EXPECTED_SKILLS = [
    "start", "why", "problem", "interview", "roleplay",
    "believers", "build-check", "pivot", "story", "pitch",
    "pmf-check", "default-alive", "gbrain",
]

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label} -- {detail}")
        failures.append(label)


print("=== SKILL FILES EXIST ===")
for skill in EXPECTED_SKILLS:
    f = SKILLS_DIR / skill / "SKILL.md"
    check(f"{skill}/SKILL.md exists", f.exists())

print("\n=== SKILL FRONTMATTER ===")
for skill in EXPECTED_SKILLS:
    f = SKILLS_DIR / skill / "SKILL.md"
    if not f.exists():
        continue
    content = f.read_text()

    check(f"{skill}: starts with ---", content.startswith("---\n"))

    try:
        fm_end = content.index("\n---\n", 4)
        fm = content[4:fm_end]
        body = content[fm_end + 5:]
    except ValueError:
        check(f"{skill}: has closing ---", False, "no '---' delimiter found")
        continue

    meta = {}
    for line in fm.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()

    check(f"{skill}: has 'name' field", "name" in meta, list(meta.keys()))
    check(f"{skill}: name matches dir", meta.get("name") == skill, f"got '{meta.get('name')}'")
    check(f"{skill}: has 'description' field", "description" in meta)
    check(f"{skill}: description >= 30 chars", len(meta.get("description", "")) >= 30)
    check(f"{skill}: body starts with #", body.lstrip().startswith("#"))
    check(f"{skill}: body has 'brain/'", "brain/" in body)

print("\n=== RESULT ===")
if failures:
    print(f"  {len(failures)} FAILURES:")
    for f in failures:
        print(f"    - {f}")
    sys.exit(1)
else:
    print("  ALL CHECKS PASSED")
