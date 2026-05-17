# 05AI-级联催化逆合成

## 基本信息

| 字段 | 内容 |
|---|---|
| 项目方向 | 生物催化/化学酶级联反应数据库、反应步骤结构化、催化剂与条件建模 |
| 当前状态 | 已形成 Cascade Dataset v4 结构化数据库和数据 release 设计 |
| 负责人/参与者 | 待填写 |
| 更新时间 | 待填写 |

## 研究问题

级联催化和化学酶级联反应常常把多个反应步骤整合在一个合成流程中，但文献中的反应步骤、催化剂、底物范围、条件和产率信息分散在正文、补充材料、表格和图注中，难以直接用于建模和路线分析。

本项目的核心问题是：如何把这些分散的级联反应信息整理成可审计、可筛选、可建模的结构化数据库，并进一步支持反应路径设计、催化剂选择、条件分析和逆合成相关任务。

## 研究意义

这个项目虽然偏化学合成，但与生物方向中的酶催化、生物制造、药物合成路线和候选分子制备都有联系。它能展示团队把复杂文献知识转化为结构化数据资源的能力。

对 panel 来说，它可以作为“数据资源建设 + 生物催化/化学酶级联任务”的代表，重点展示已经形成的结构化数据库、质量分层和 release 体系。

## 项目目标

- 完成 Cascade Dataset v4 的数据结构说明和质量分层描述。
- 明确 gold/silver/bronze/quarantine 四级质量体系和默认高质量子集。
- 支持后续反应级建模、步骤级 transformation prediction、催化剂选择、条件建模和底物范围分析。
- 为老师展示数据规模、字段覆盖、质量控制和可用任务。

## 技术路线

1. 从 primary articles 和 supplementary information 中整理级联反应记录。
2. 将反应结构拆分为 reactions、steps、catalysts、species、substrate_scope 等规范表。
3. 对记录进行质量分层：gold、silver、bronze、quarantine。
4. 使用补充材料 enrichment 补齐产率、时间、温度、pH、buffer、solvent 和 substrate-scope 等字段。
5. 形成 flat CSV、nested JSONL 和 normalized SQLite 三类 release 形态。
6. 根据任务类型选择筛选策略：严格建模用 gold，默认分析用 gold+silver，分子建模需过滤 SMILES 完整性，工艺变量建模需过滤温度/pH/溶剂/时间完整性。

## 当前进展

本项目已经完成较系统的数据集建设和描述：

- 全量数据库包含 3810 条 cascade reaction records，来自 2498 个 unique DOI。
- 默认高质量 release 包含 3744 条 gold/silver 反应，来自 2464 个 DOI。
- 结构化后包含 8609 个 steps、9444 个 catalyst components、21225 个 input/output species records、3458 个 substrate-scope entries。
- 质量分层为 2885 条 gold、859 条 silver、60 条 bronze、6 条 quarantine。
- supplementary-information enrichment 已为 886 行增加至少一个新字段，包括 246 个 overall yields、173 个 total reaction-time、376 个 step reaction-time 和 2550 个 substrate-scope entries。
- 技术验证显示无 JSON parse-error 和编码 artifact flag；target product names 覆盖 99.90%，starting material names 覆盖 99.79%，starting material SMILES 覆盖 89.13%，target product SMILES 覆盖 80.08%。
- 反应步骤以 oxidation、reduction、C-C coupling、racemization、acylation、amination、hydrolysis 等为主；催化剂以 enzyme 为主，也包括 metal catalyst、organocatalyst、whole-cell、photocatalyst 等。

