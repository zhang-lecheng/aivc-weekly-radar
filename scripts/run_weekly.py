#!/usr/bin/env python3
"""Deterministic fetch/validate/publish boundary for the DeepSeek weekly task.

DeepSeek Harness supplies screened records through --screened-json. This script
never asks a model to hold GitHub credentials and only advances state after a
successful commit and push.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "data/run-state.json"
PAPERS = ROOT / "data/papers.jsonl"
DATE = dt.datetime.now(dt.timezone.utc).date().isoformat()

def load_json(path, default):
    try: return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError): return default

def canonical(p):
    for key in ("doi", "arxiv_id", "pmid"):
        value = str(p.get(key, "")).strip().lower()
        if value: return f"{key}:{value.replace('https://doi.org/','')}"
    title = re.sub(r"[^a-z0-9]+", " ", str(p.get("title", "")).lower()).strip()
    return "title:" + hashlib.sha256(title.encode()).hexdigest()[:24]

def fetch_arxiv(since):
    q = ' OR '.join(f'all:"{x}"' for x in ("virtual cell", "cell fate design", "perturbation response", "multimodal perturbation", "inverse design cell"))
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": q, "start": 0, "max_results": 100, "sortBy": "submittedDate", "sortOrder": "descending"})
    req = urllib.request.Request(url, headers={"User-Agent": "aivc-weekly-radar/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r: raw = r.read().decode("utf-8", "replace")
    records = []
    for block in re.findall(r"<entry>(.*?)</entry>", raw, re.S):
        def tag(name):
            m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", block, re.S); return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
        published = tag("published")[:10]
        if published >= since:
            records.append({"title": re.sub(r"\s+", " ", tag("title")), "abstract": re.sub(r"\s+", " ", tag("summary")), "arxiv_id": tag("id").rsplit("/",1)[-1], "dates": [published], "urls": [tag("id")], "source": "arXiv"})
    return records

def read_screened(path):
    if not path: return []
    value = json.loads(Path(path).read_text())
    if isinstance(value, dict): value = value.get("papers", [])
    if not isinstance(value, list): raise ValueError("screened JSON must be a list or {papers:list}")
    return value

def validate(records):
    out, seen = [], set()
    required = {"title", "innovation_score", "score_breakdown", "confidence", "category", "relevance_to_project"}
    for p in records:
        if not required.issubset(p): raise ValueError(f"missing fields in screened record: {p.get('title','<untitled>')}")
        score = int(p["innovation_score"])
        limits = {"question_shift":30, "decision_or_experiment_shift":20, "information_shift":15, "evaluation_shift":15, "evidence_strength":15, "nontriviality":5}
        breakdown = p["score_breakdown"]
        if set(breakdown) != set(limits) or any(not isinstance(breakdown[k], int) or not 0 <= breakdown[k] <= v for k,v in limits.items()): raise ValueError("invalid score breakdown")
        if sum(breakdown.values()) != score: raise ValueError("score must equal sum of breakdown")
        if not 0 <= score <= 100: raise ValueError(f"bad score for {p['title']}")
        p = dict(p); p["canonical_id"] = p.get("canonical_id") or canonical(p); p["last_seen"] = DATE
        if p["canonical_id"] in seen: continue
        seen.add(p["canonical_id"]); out.append(p)
    return sorted(out, key=lambda x: (-int(x["innovation_score"]), x["title"].lower()))

def write_week(records, since, dry_run):
    week = ROOT / "weekly" / f"{DATE}.md"
    main = [p for p in records if p.get("list_status") == "main" and p["score_breakdown"]["evidence_strength"] > 0][:8]
    observe = [p for p in records if p not in main][:4]
    lines = [f"# AIVC 每周文献雷达｜{DATE}", "", f"> 检索窗口：{since} 至 {DATE}。按研究问题/范式创新排序，不按 SOTA 排序。", ""]
    lines += ["## 本周判断", "本周结果由 DeepSeek Harness 的证据审查生成；主榜单只保留有可核对实证证据的新问题或新范式。", "", "## 主榜单"]
    if not main: lines += ["", "本周没有足够证据支持的新范式论文。"]
    for i,p in enumerate(main,1):
        lines += [f"", f"### {i}. {p['title']}（{p['innovation_score']}/100）", f"- 链接：{p.get('urls',[''])[0]}", f"- 类别：{p['category']}；置信度：{p['confidence']}", f"- 分项：`{json.dumps(p['score_breakdown'], ensure_ascii=False)}`", f"- 新问题：{p.get('one_line_question','')}", f"- 中文简介：{p.get('summary_zh','')}", f"- 证据与限制：{p.get('evidence_limit','')}", f"- 与本项目：{p['relevance_to_project']}", f"- 建议动作：{p.get('recommended_action','')}" ]
    lines += ["", "## 观察区"]
    for p in observe: lines += [f"- **{p['title']}**（{p['innovation_score']}/100）：{p.get('observation_reason','暂不满足主榜单证据标准。')} {p.get('urls',[''])[0]}"]
    lines += ["", "## 追踪", "- 新增主题与版本更新由本次筛选记录保留。", "- 下周继续核查：独立重复、留出条件、真实前瞻实验闭环。"]
    if not dry_run: week.write_text("\n".join(lines)+"\n")
    return week, main

def update_index(main):
    idx = ROOT / "INDEX.md"; old = idx.read_text() if idx.exists() else "# AIVC Weekly Radar Index\n"
    line = f"- [{DATE}](weekly/{DATE}.md)：主榜单 {len(main)} 篇；最高分：{main[0]['title']}（{main[0]['innovation_score']}）" if main else f"- [{DATE}](weekly/{DATE}.md)：没有足够证据支持的新范式论文"
    if line not in old: idx.write_text(old.rstrip()+"\n\n"+line+"\n")

def publish(repo):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token: raise RuntimeError("missing GITHUB_TOKEN/GH_TOKEN; publication stopped before commit")
    # Token is passed through git credential helper, never command arguments or remote URL.
    env = os.environ.copy(); env["GIT_TERMINAL_PROMPT"] = "0"
    subprocess.run(["git", "add", "README.md", "INDEX.md", "weekly", "data", "sources.md", "rubric.md", "scripts"], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    subprocess.run(["git", "commit", "-m", f"weekly AIVC radar: {DATE}"], cwd=ROOT, check=False)
    remote = f"https://github.com/{repo}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote], cwd=ROOT, check=False)
    # git credential protocol avoids exposing token in process args and config.
    ask = "protocol=https\nhost=github.com\n\n"
    cred = subprocess.run(["git", "-c", "credential.helper=cache --timeout=60", "push", "-u", "origin", "HEAD"], cwd=ROOT, env={**env, "GIT_ASKPASS": str(ROOT/"scripts/git-askpass.sh")}, check=False)
    if cred.returncode: raise RuntimeError("git push failed; state was not advanced")

def publish_state(repo):
    """Commit the success checkpoint only after the content push succeeded."""
    subprocess.run(["git", "add", "data/run-state.json"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"record successful AIVC radar run: {DATE}"], cwd=ROOT, check=False)
    env = os.environ.copy(); env["GIT_TERMINAL_PROMPT"] = "0"
    cred = subprocess.run(["git", "-c", "credential.helper=cache --timeout=60", "push", "origin", "HEAD"], cwd=ROOT, env={**env, "GIT_ASKPASS": str(ROOT/"scripts/git-askpass.sh")}, check=False)
    if cred.returncode: raise RuntimeError("success checkpoint push failed; content is published but checkpoint remains local")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo"); ap.add_argument("--since"); ap.add_argument("--screened-json"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--publish", action="store_true"); a=ap.parse_args()
    state=load_json(STATE,{}) ; since=a.since or state.get("last_successful_run") or (dt.date.today()-dt.timedelta(days=14)).isoformat()
    source_errors = []
    try: fetched=fetch_arxiv(since)
    except Exception as e: source_errors.append(str(e)); print(f"source_error: {e}", file=sys.stderr); fetched=[]
    records=validate(read_screened(a.screened_json)) if a.screened_json else []
    if records:
        if not a.dry_run:
            existing={json.loads(x).get("canonical_id") for x in PAPERS.read_text().splitlines() if x.strip()}
            with PAPERS.open("a") as f:
                for p in records:
                    if p["canonical_id"] not in existing: f.write(json.dumps(p,ensure_ascii=False)+"\n")
        week,main=write_week(records,since,a.dry_run); update_index(main) if not a.dry_run else None
    else: week,main=write_week([],since,a.dry_run)
    if fetched and not a.dry_run:
        (ROOT / 'data' / f'candidates-{DATE}.json').write_text(json.dumps(fetched,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({"date":DATE,"since":since,"fetched":len(fetched),"screened":len(records),"main":len(main),"dry_run":a.dry_run,"source_errors":source_errors},ensure_ascii=False))
    if a.publish and not a.dry_run:
        if not a.repo: raise SystemExit("--repo is required with --publish")
        publish(a.repo)
        state.update({"last_successful_run":DATE,"last_attempt":DATE,"last_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()}); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
        publish_state(a.repo)
    else: state["last_attempt"]=DATE; STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n") if not a.dry_run else None
if __name__ == "__main__": main()
