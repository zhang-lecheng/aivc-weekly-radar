# DeepSeek Harness 每周任务提示词

模型固定为 `westlake/deepseek-flash`。每周运行时读取本项目的 `data/run-state.json`，检索上次成功日期之后的新公开/新修订论文；首次运行取最近 14 天。先用 arXiv、Europe PMC、bioRxiv 和公开期刊页面收集候选，再核对摘要、正文、split、重复数和实验闭环。

只把改变研究对象、实验/决策、信息条件、评价目标或可证伪性要求的工作放进主榜单。普通 backbone、loss、benchmark SOTA、只有观点没有证据的论文放观察区。使用 [`rubric.md`](rubric.md) 的六项分数，按 `innovation_score` 降序，主榜单最多 8 篇，观察区最多 4 篇。中文简介 100--180 字；所有数值附直接论文链接和原文位置。证据不足时降低 `evidence_strength` 和 `confidence`，不得猜测。

## 输出协议

把筛选结果写成临时 JSON 文件，结构必须符合 [`data/screened-record.schema.json`](data/screened-record.schema.json)，每个对象至少包含：

```json
{
  "title": "论文标题",
  "doi": "可选",
  "arxiv_id": "可选",
  "dates": ["YYYY-MM-DD"],
  "urls": ["https://..."],
  "innovation_score": 0,
  "score_breakdown": {"question_shift": 0, "decision_or_experiment_shift": 0, "information_shift": 0, "evaluation_shift": 0, "evidence_strength": 0, "nontriviality": 0},
  "confidence": "high|medium|low",
  "list_status": "main|observe",
  "category": "直接竞争|可迁移方法|问题启发|数据/平台资源|低相关",
  "relevance_to_project": "具体说明与跨背景扰动、稀缺功能读出和 AI4Science 项目的关系及风险",
  "summary_zh": "100--180 字中文简介",
  "one_line_question": "一句话新问题",
  "evidence_limit": "证据和限制",
  "recommended_action": "下一步动作",
  "tags": ["multimodal"]
}
```

保存后由外层执行：

```bash
python3 scripts/run_weekly.py --screened-json /tmp/aivc-screened.json --repo OWNER/REPO --publish
```

脚本负责规范化、去重、生成 `weekly/YYYY-MM-DD.md`、更新 `INDEX.md` 和 `data/papers.jsonl`、校验并提交推送。GitHub 凭据只能由运行环境注入 `GITHUB_TOKEN` 或 `GH_TOKEN`；不要在模型输出、提示词、文件、commit 或 URL 中出现 PAT。推送失败必须停止并返回失败原因，不能推进 `last_successful_run`。
