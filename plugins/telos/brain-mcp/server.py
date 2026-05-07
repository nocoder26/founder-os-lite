#!/usr/bin/env python3
"""
Telos — Brain MCP server

Exposes the markdown brain as queryable MCP tools.
Stdio transport. Configured via .mcp.json at project root.

Run: python brain-mcp/server.py
Requires: pip install mcp
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from datetime import date
import os
import re

mcp = FastMCP("telos-brain")

# Resolve brain dir. Defaults to ./brain relative to wherever Claude Code runs.
# Can be overridden via BRAIN_DIR env var (set in .mcp.json if needed).
BRAIN_DIR = Path(os.environ.get("BRAIN_DIR", "brain")).resolve()


# ---------- helpers ----------

def _read(file: Path) -> str:
    if not file.exists():
        return ""
    return file.read_text()


def _write(file: Path, content: str) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)


def _safe_filename(name: str) -> str:
    """Strip path components and reject traversal. Returns just the basename.

    Prevents `add_interview('../../../tmp/evil.md', ...)` and friends from
    writing outside BRAIN_DIR. Caller MUST handle ValueError.
    """
    if not name:
        raise ValueError("filename cannot be empty")
    base = Path(name).name
    if not base or base in (".", ".."):
        raise ValueError(f"invalid filename: {name!r}")
    if "/" in base or "\\" in base or "\x00" in base:
        raise ValueError(f"filename contains path separators: {name!r}")
    return base


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML-ish frontmatter from a markdown file. Returns {} if none."""
    if not content.startswith("---"):
        return {}
    try:
        fm_end = content.index("---", 3)
        fm = content[3:fm_end]
        meta = {}
        for line in fm.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta
    except ValueError:
        return {}


# ---------- stage management ----------

@mcp.tool()
def get_stage() -> str:
    """Get the current stage from brain/stage.md. Returns '0', '1', '2', '3', or '4'.

    Defends against corrupted stage.md by validating the value — out-of-range
    or non-numeric stage values fall back to '0'.
    """
    content = _read(BRAIN_DIR / "stage.md")
    valid = {"0", "1", "2", "3", "4"}
    for line in content.split("\n"):
        if line.startswith("current:"):
            val = line.split(":", 1)[1].strip()
            return val if val in valid else "0"
    return "0"


@mcp.tool()
def set_stage(new_stage: str, reason: str) -> str:
    """Update the current stage. Stage must be 0-4. Reason is logged to history."""
    if new_stage not in ["0", "1", "2", "3", "4"]:
        return f"Error: stage must be 0-4, got '{new_stage}'"

    file = BRAIN_DIR / "stage.md"
    content = _read(file)
    today = str(date.today())

    if "current:" in content:
        new_content = re.sub(
            r"^current:.*$", f"current: {new_stage}", content, count=1, flags=re.MULTILINE
        )
    else:
        new_content = f"# Stage\n\ncurrent: {new_stage}\n\n## History\n"

    if "## History" in new_content:
        new_content = new_content.replace(
            "## History",
            f"## History\n\n- {today} — moved to stage {new_stage}: {reason}",
            1,
        )
    else:
        new_content += f"\n## History\n\n- {today} — moved to stage {new_stage}: {reason}\n"

    _write(file, new_content)
    return f"Stage updated to {new_stage}"


# ---------- problem ----------

@mcp.tool()
def get_problem() -> str:
    """Read the current problem hypothesis from brain/problem.md."""
    return _read(BRAIN_DIR / "problem.md")


@mcp.tool()
def update_problem(content: str) -> str:
    """Replace brain/problem.md with new content. Caller assembles the markdown."""
    _write(BRAIN_DIR / "problem.md", content)
    return "Problem hypothesis updated"


# ---------- why ----------

@mcp.tool()
def get_why() -> str:
    """Read the founder's motivation from brain/why.md. Surfaces 'what would make me quit' anchor."""
    return _read(BRAIN_DIR / "why.md")


@mcp.tool()
def update_why(content: str) -> str:
    """Replace brain/why.md with new content."""
    _write(BRAIN_DIR / "why.md", content)
    return "Motivation updated"


@mcp.tool()
def append_journey(date_str: str, context: str, trigger: str, response: str) -> str:
    """Append an entry to brain/journey.md (the founder's emotional record)."""
    file = BRAIN_DIR / "journey.md"
    content = _read(file)
    if not content:
        content = "# Journey\n\nA log of the moments when discipline, doubt, or decisions came up.\n"

    entry = f"\n## {date_str} — {context}\nTrigger: {trigger}\nResponse: {response}\n"
    _write(file, content + entry)
    return "Journey entry appended"


# ---------- interviews ----------

@mcp.tool()
def list_interviews() -> list[dict]:
    """List all interview files in brain/interviews/ with metadata from frontmatter."""
    interviews_dir = BRAIN_DIR / "interviews"
    if not interviews_dir.exists():
        return []

    results = []
    for file in sorted(interviews_dir.glob("*.md")):
        if file.name.startswith("."):
            continue
        meta = _parse_frontmatter(file.read_text())
        results.append({
            "file": file.name,
            "date": meta.get("date", ""),
            "participant": meta.get("participant", ""),
            "classification": meta.get("classification", "").upper(),
            "recruited_via": meta.get("recruited_via", ""),
        })
    return results


@mcp.tool()
def get_interview(filename: str) -> str:
    """Read a specific interview file from brain/interviews/."""
    file = BRAIN_DIR / "interviews" / filename
    if not file.exists():
        return f"Error: {filename} not found in brain/interviews/"
    return file.read_text()


@mcp.tool()
def add_interview(filename: str, content: str) -> str:
    """Create a new interview file in brain/interviews/. Filename should not include path."""
    try:
        filename = _safe_filename(filename)
    except ValueError as e:
        return f"Error: {e}"
    if not filename.endswith(".md"):
        filename += ".md"
    file = BRAIN_DIR / "interviews" / filename
    if file.exists():
        return f"Error: {filename} already exists. Use a different filename."
    _write(file, content)
    return f"Interview saved: brain/interviews/{filename}"


# ---------- evidence ----------

@mcp.tool()
def list_evidence() -> list[str]:
    """List all evidence files in brain/evidence/."""
    evidence_dir = BRAIN_DIR / "evidence"
    if not evidence_dir.exists():
        return []
    return [f.name for f in sorted(evidence_dir.glob("*.md")) if not f.name.startswith(".")]


@mcp.tool()
def add_evidence(filename: str, content: str) -> str:
    """Create a new evidence file in brain/evidence/."""
    try:
        filename = _safe_filename(filename)
    except ValueError as e:
        return f"Error: {e}"
    if not filename.endswith(".md"):
        filename += ".md"
    file = BRAIN_DIR / "evidence" / filename
    if file.exists():
        return f"Error: {filename} already exists. Use a different filename."
    _write(file, content)
    return f"Evidence saved: brain/evidence/{filename}"


@mcp.tool()
def query_evidence(keywords: list[str]) -> list[dict]:
    """Search across brain/evidence/ for entries matching any of the keywords. Returns ranked matches with snippets."""
    evidence_dir = BRAIN_DIR / "evidence"
    if not evidence_dir.exists():
        return []

    keywords_lower = [k.lower() for k in keywords]
    results = []

    for file in sorted(evidence_dir.glob("*.md")):
        if file.name.startswith("."):
            continue
        content = file.read_text()
        content_lower = content.lower()
        matches = sum(1 for k in keywords_lower if k in content_lower)
        if matches > 0:
            snippet = ""
            for k in keywords_lower:
                idx = content_lower.find(k)
                if idx >= 0:
                    start = max(0, idx - 60)
                    end = min(len(content), idx + 180)
                    snippet = content[start:end].replace("\n", " ")
                    break
            results.append({
                "file": file.name,
                "matches": matches,
                "snippet": snippet,
            })

    return sorted(results, key=lambda x: -x["matches"])


# ---------- believers ----------

@mcp.tool()
def get_believers_index() -> str:
    """Read brain/believers/index.md."""
    return _read(BRAIN_DIR / "believers" / "index.md")


@mcp.tool()
def update_believers_index(content: str) -> str:
    """Replace brain/believers/index.md with new content."""
    _write(BRAIN_DIR / "believers" / "index.md", content)
    return "Believers index updated"


@mcp.tool()
def believer_density() -> dict:
    """Calculate believer density and segment concentration from interviews. Returns metrics + verdict."""
    interviews = list_interviews()
    total = len(interviews)

    if total == 0:
        return {
            "total_interviews": 0,
            "believer_count": 0,
            "neutral_count": 0,
            "infidel_count": 0,
            "density_pct": 0.0,
            "verdict": "no interviews yet — run /interview",
        }

    believers = [i for i in interviews if i.get("classification") == "BELIEVER"]
    neutrals = [i for i in interviews if i.get("classification") == "NEUTRAL"]
    infidels = [i for i in interviews if i.get("classification") == "INFIDEL"]

    density = (len(believers) / total) * 100

    if total < 5:
        verdict = f"too few interviews ({total}) to assess — keep going"
    elif density >= 50:
        verdict = "STRONG believer density (≥50%) — focused niche, ready to advance"
    elif density >= 30:
        verdict = "HEALTHY believer density (≥30%)"
    elif density >= 15:
        verdict = "WEAK — refine targeting or hypothesis"
    else:
        verdict = "PMF MIRAGE risk — most users are tire-kickers"

    return {
        "total_interviews": total,
        "believer_count": len(believers),
        "neutral_count": len(neutrals),
        "infidel_count": len(infidels),
        "density_pct": round(density, 1),
        "verdict": verdict,
    }


# ---------- runway ----------

@mcp.tool()
def get_runway() -> str:
    """Read brain/runway.md (cash, burn, growth, default-alive status)."""
    return _read(BRAIN_DIR / "runway.md")


@mcp.tool()
def update_runway(content: str) -> str:
    """Replace brain/runway.md with new content."""
    _write(BRAIN_DIR / "runway.md", content)
    return "Runway updated"


# ---------- decisions ----------

@mcp.tool()
def get_decisions() -> str:
    """Read brain/decisions.md (every product decision logged with evidence)."""
    return _read(BRAIN_DIR / "decisions.md")


@mcp.tool()
def log_decision(date_str: str, feature: str, evidence: str, decision: str, reasoning: str) -> str:
    """Append a new decision entry to brain/decisions.md.

    Args:
        date_str: Date of decision (ISO format YYYY-MM-DD)
        feature: One-liner of the feature/change
        evidence: Citations into brain/evidence/ or brain/interviews/, comma-separated
        decision: One of: build | defer | drop | speculative | manual_override
        reasoning: One paragraph explaining the call
    """
    file = BRAIN_DIR / "decisions.md"
    content = _read(file)
    stage = get_stage()

    entry = (
        f"\n\n## {date_str} — {feature}\n"
        f"Evidence: {evidence}\n"
        f"Decision: {decision}\n"
        f"Stage: {stage}\n"
        f"Reasoning: {reasoning}\n"
    )

    _write(file, content + entry)
    return "Decision logged"


# ---------- meta ----------

@mcp.tool()
def brain_status() -> dict:
    """One-shot snapshot of the founder's brain state. Use this to ground every session."""
    interviews = list_interviews()
    density = believer_density()

    problem = _read(BRAIN_DIR / "problem.md")
    why = _read(BRAIN_DIR / "why.md")

    return {
        "stage": get_stage(),
        "problem_hypothesis_set": bool(problem.strip()) and "(empty" not in problem,
        "why_set": bool(why.strip()) and "(empty" not in why,
        "interviews": len(interviews),
        "believers": density["believer_count"],
        "believer_density_pct": density["density_pct"],
        "evidence_files": len(list_evidence()),
        "verdict": density["verdict"],
    }


if __name__ == "__main__":
    mcp.run()
