#!/usr/bin/env python3
"""Build the public dashboard's compact data snapshot from the research ledger."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def main():
    papers = []
    source = ROOT / "data/papers.jsonl"
    if source.exists():
        for line in source.read_text().splitlines():
            if line.strip():
                papers.append(json.loads(line))

    issues = []
    for path in sorted((ROOT / "weekly").glob("*.md"), reverse=True):
        text = path.read_text()
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        scores = [int(x) for x in re.findall(r"\（(\d{1,3})/100\）", text)]
        issues.append({
            "date": path.stem,
            "title": title,
            "main_count": len(re.findall(r"^### \d+\.", text, re.M)),
            "top_score": max(scores, default=0),
            "url": f"https://github.com/zhang-lecheng/aivc-weekly-radar/blob/master/weekly/{path.name}",
        })

    state_path = ROOT / "data/run-state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    payload = {
        "updated_at": state.get("last_successful_run", ""),
        "papers": sorted(papers, key=lambda p: (-int(p.get("innovation_score", 0)), p.get("title", "").lower())),
        "issues": issues,
    }
    DOCS.mkdir(exist_ok=True)
    (DOCS / "dashboard.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
