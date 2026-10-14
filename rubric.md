# 创新性评分规则

`innovation_score` 为以下分项之和（0--100）：

| 分项 | 权重 | 问题 |
|---|---:|---|
| question_shift | 0--30 | 研究对象或科学问题是否离开标准 RNA 扰动预测 |
| decision_or_experiment_shift | 0--20 | 是否改变干预选择、实验设计或科学决策 |
| information_shift | 0--15 | 是否引入实质不同的信息条件或跨模态互补 |
| evaluation_shift | 0--15 | 是否用科学分辨率、命中、校准、风险或输入贡献约束主张 |
| evidence_strength | 0--15 | 外部数据、留出条件、独立重复、前瞻实验闭环 |
| nontriviality | 0--5 | 是否不是既有路线换名或直接拼接 |

分数表达研究问题和范式的创新性，不表达论文总体质量。`confidence` 单独记录证据完整程度；证据不足时 `evidence_strength` 必须低。

## 进入主榜单

至少一项 question/decision/information/evaluation shift 为正，并且存在可核对的实证证据。只有架构、loss 或 benchmark 提升；只在同一数据集换模型；只有观点且无可执行验证；新闻稿或搜索摘要；这些都只能进入观察区。

每次必须区分细胞数、扰动数、条件数、重复数和独立实验数；回顾性 replay、仿真、体外实验和前瞻验证不能混写。
