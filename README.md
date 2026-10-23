# AIVC Weekly Radar

**English** | [简体中文](README.zh-CN.md)

**[Explore the research dashboard](https://zhang-lecheng.github.io/aivc-weekly-radar/)**

A weekly reading radar for AI Virtual Cell (AIVC) research that changes scientific questions, experimental decisions, or evaluation practices. Innovation scores reflect these changes rather than model size, venue prestige, or gains on an existing benchmark.

## Updates and reading

DeepSeek Harness runs every **Monday at 09:00, Asia/Shanghai**, using `westlake/deepseek-flash`. Each issue includes up to eight featured papers and four watchlist entries, with Chinese summaries, score breakdowns, evidence limitations, and direct source links. Quiet weeks receive a short issue rather than a padded ranking.

- [Public dashboard](https://zhang-lecheng.github.io/aivc-weekly-radar/): featured papers, search, filters, and issue archives.
- [Issue index](INDEX.md) and [weekly reports](weekly/): findings and editorial judgments for each week.
- [Scoring rubric](rubric.md) and [sources](sources.md): selection criteria, queries, and evidence requirements.
- [Structured paper archive](data/papers.jsonl): one machine-readable record per paper.

Weekly reports and the dashboard are currently in Chinese. The repository overview is available in both languages through the links above.

## Research focus

The radar supports AI4Science and virtual-cell research, with an emphasis on functional readouts, intervention selection, multimodal information, temporal and experimental feedback, falsifiability, and audits of input contributions. Public data and computational experiments should support the main findings; collaborative wet-lab experiments can provide additional validation.

## Run locally

```bash
python3 scripts/run_weekly.py --dry-run
python3 scripts/run_weekly.py --screened-json /path/to/screened.json --publish --repo OWNER/REPO
```

DeepSeek Harness handles screening and evidence review. Local scripts collect and normalize records, deduplicate and validate entries, regenerate dashboard data, and commit and push updates. Publishing reads `GITHUB_TOKEN` or `GH_TOKEN` from the environment. Credentials are kept out of prompts, files, remote URLs, and logs. A failed push does not advance the successful-run checkpoint.

## Repository layout

| Path | Contents |
| --- | --- |
| `README.md` / `README.zh-CN.md` | English overview and Chinese translation, linked at the top |
| `weekly/` / `INDEX.md` | Chinese weekly reports and their index |
| `data/papers.jsonl` | Structured paper records |
| `docs/` | GitHub Pages dashboard and generated data |
| `scripts/` | Collection, validation, and publishing code |

Paper suggestions and corrections are welcome. Please include a direct source link and the evidence supporting your suggestion.
