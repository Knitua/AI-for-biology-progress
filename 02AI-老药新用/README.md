# 02AI-老药新用

## 基本信息

| 字段 | 内容 |
|---|---|
| 项目方向 | FDA 已批准小分子、癌症相关靶点筛选、老药新用候选排序 |
| 当前状态 | 已完成 Step 1-5 大规模筛选和 Top1000 结构增强，具备阶段性展示结果 |
| 负责人/参与者 | 待填写 |
| 更新时间 | 2026-05-11 |

## 研究问题

本项目要解决的是：在 FDA 已批准小分子药物中，哪些药物可能与癌症相关人类蛋白靶点形成值得进一步验证的 drug-target pair？这些候选是否同时具备相互作用预测、疾病证据、网络证据和结构对接支持？

当前重点不是泛泛讨论“老药新用”，而是基于 BioMaster 流程结果，把候选药物、靶点、疾病证据、结构增强结果和后续验证优先级整理成老师可以判断的阶段性成果。

## 研究意义

老药新用的优势在于药物安全性、可获得性和转化路径相对清晰。对于团队来说，这个项目已经有大规模计算筛选结果，可以作为最容易向老师展示“已有量化进展”的项目之一。

该项目也能作为后续疾病方向或具体癌种方向的候选入口：先从 pan-cancer 筛选得到高优先级 pair，再根据癌种、机制、药物可及性和实验可行性做二次筛选。

## 项目目标

- 将 BioMaster Top 候选整理成结构化表格。
- 区分 Step 1-5 screening 已完成、Top1000 structural enhancement 已完成、full DiffDock 尚未完成这三类状态。
- 从 Stage 6 Top100 中筛选 20-50 个适合进一步验证的候选 pair。
- 为老师汇报准备一页结果：筛选规模、证据整合方式、Top 候选、限制和下一步。

## 技术路线

1. FDA-approved drug library：915 个小分子，均有 SMILES、InChIKey、分子式和 SDF，913 个有 PubChem CID。
2. Human protein target library：1000 个蛋白靶点，1000 个有序列，998 个有 AlphaFold receptor 文件。
3. ConPLex：完成 915000 个 drug-target pair 的第一层相互作用/亲和力预测。
4. Disease evidence integration：整合 Open Targets、STRING 和 TxGNN，形成癌症导向疾病证据排序。
5. Stage 5 ranking：对 915000 个 pair 生成疾病证据融合排序。
6. Stage 6 structural enhancement：对 Top1000 做 DiffDock 结构增强，940/1000 有有效输出，并形成 Stage 6 consensus ranking。

## 当前进展

本项目已经形成明确的阶段性计算筛选成果：

- 完成 915 个 FDA 已批准小分子 × 1000 个人类蛋白靶点的筛选，共 915000 个 drug-target pair。
- Step 1-5 report-scale screening 已完成，所有 pair 都有 ConPLex 预测，并完成 Open Targets、STRING、TxGNN 证据整合。
- Stage 5 Top1000 覆盖 337 个 unique drugs 和 64 个 unique proteins，Top1000 均有直接或网络疾病证据。
- Stage 6 Top1000 结构增强已完成，940/1000 个 pair 有 DiffDock 输出。
- Stage 6 Top100 包含 67 个 unique drugs 和 20 个 unique proteins，其中 88/100 有 DiffDock 输出。
- Stage 5 Top 候选包括 Afatinib Dimaleate-EGFR、Pazopanib Hydrochloride-KIT、Dacomitinib-EGFR、Osimertinib Mesylate-EGFR、Cabozantinib S-Malate-KIT 等。
- Full DiffDock 尚未完成：913170 个 DiffDock-ready pair 中已处理 233500 个，进度 25.57%；当前队列未运行，磁盘使用率 92.38%，需要先清理磁盘和设计失败任务重跑策略。

