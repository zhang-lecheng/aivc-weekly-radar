# AIVC Weekly Radar

[English](README.md) | **简体中文**

**[浏览学术看板](https://zhang-lecheng.github.io/aivc-weekly-radar/)**

每周追踪 AI Virtual Cell（AIVC）中改变研究问题、实验决策和评价方式的工作。创新分用于衡量研究问题和研究方式的变化，不以模型大小、论文声望或同一基准的最高分作为排序依据。

## 更新与阅读

DeepSeek Harness 每周一 09:00（Asia/Shanghai）执行更新，使用 `westlake/deepseek-flash`。主榜最多 8 篇，观察区最多 4 篇；每篇附中文简介、评分分项、证据限制和来源链接。没有足够证据时发布短报。

- [公开看板](https://zhang-lecheng.github.io/aivc-weekly-radar/)：重点论文、搜索筛选与历期入口。
- [周报索引](INDEX.md)与[历期周报](weekly/)：每周的具体发现和判断。
- [评分规则](rubric.md)与[检索来源](sources.md)：收录范围、查询方式及证据要求。
- [结构化文献库](data/papers.jsonl)：一篇论文一行的机器可读记录。

## 项目定位

本项目服务于 AI4Science 和虚拟细胞研究，关注功能读出、干预选择、多组学信息、时间与实验反馈，以及模型的可证伪性和输入贡献审计。公开数据与计算实验应能支持主要结论，合作湿实验用于补充验证。

## 运行

```bash
python3 scripts/run_weekly.py --dry-run
python3 scripts/run_weekly.py --screened-json /path/to/screened.json --publish --repo OWNER/REPO
```

DeepSeek Harness 负责筛选和证据核查；本地脚本负责采集、规范化、去重、校验、生成看板快照和提交推送。发布时从环境变量 `GITHUB_TOKEN` 或 `GH_TOKEN` 读取凭据，凭据不进入提示词、文件、远程 URL 或日志。推送失败时不推进成功日期。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `README.md` / `README.zh-CN.md` | 英文主页与中文说明，顶部可互相切换 |
| `weekly/` / `INDEX.md` | 中文周报与索引 |
| `data/papers.jsonl` | 结构化文献记录 |
| `docs/` | GitHub Pages 看板及生成数据 |
| `scripts/` | 采集、校验与发布程序 |

欢迎提供论文和更正，并附原文链接及具体依据。
