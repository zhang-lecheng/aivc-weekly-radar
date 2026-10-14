# 来源与运行规则

## 来源

优先查询 arXiv、bioRxiv、medRxiv、Europe PMC/PubMed 及 Cell、Nature、Nature Methods、Nature Biotechnology、Science、Cell Systems、Genome Biology、NeurIPS、ICML、ICLR、RECOMB、ML4Bio 的公开页面。查询词包括 `virtual cell`、`AI virtual cell`、`single-cell perturbation`、`cell fate design`、`multimodal perturbation`、`proteomics perturbation`、`metabolomics perturbation`、`active experimental design`、`inverse design cell`。

## 版本和失败纪律

同一 arXiv/bioRxiv/期刊工作按 DOI、arXiv ID、PMID 和规范化标题去重，保留版本历史。抓取失败会记录在本次运行日志，不能静默变成“没有论文”。远程仓库不存在、凭据缺失、鉴权失败或 push 失败时，停止发布并返回非零状态；不会创建替代仓库。

更新时间由 `run_weekly.py` 写入 `data/run-state.json`，仅在成功更新并推送后推进 `last_successful_run`。重复运行同一窗口不会产生重复记录或重复提交。

## 运行日志

自动任务应在每次周刊底部注明检索窗口、成功/失败来源数和验证状态。凭据只能来自环境或 Harness 凭据存储。
