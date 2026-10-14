# AIVC Weekly Radar

每周追踪 AI Virtual Cell（AIVC）中真正改变研究问题或实验范式的工作。这里的分数衡量**问题创新性**，不是模型大小、论文声望或同一 benchmark 的 SOTA。

## 运行

```bash
python3 scripts/run_weekly.py --dry-run
python3 scripts/run_weekly.py --publish --repo OWNER/REPO
```

发布模式从运行环境读取 `GITHUB_TOKEN`（或 `GH_TOKEN`），绝不把凭据写入提示词、文件、URL 或日志。模型筛选由 DeepSeek Harness 负责；本地脚本负责来源抓取、规范化、去重、校验和幂等提交。

## 内容

- [`INDEX.md`](INDEX.md)：按日期和创新分数索引
- [`weekly/`](weekly/)：每周中文简报
- [`data/papers.jsonl`](data/papers.jsonl)：一篇论文一行的可机器读取记录
- [`rubric.md`](rubric.md)：评分规则与反例
- [`sources.md`](sources.md)：查询式、证据纪律和运行记录

主榜单最多 8 篇，观察区最多 4 篇。没有足够证据时发布短报，不为了凑数提升普通 SOTA 论文。

## 项目定位

这个雷达服务于 AI4Science/虚拟细胞研究：优先寻找功能目标、实验决策、跨模态信息、时间与反馈闭环、可证伪性和输入贡献审计等新问题。湿实验合作可以增强证据，但计算分析和公开数据必须能支撑主要结论。
