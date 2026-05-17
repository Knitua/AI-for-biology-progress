# 06AI-有机光伏材料

## 基本信息

| 字段 | 内容 |
|---|---|
| 项目方向 | OPV 器件性能数据库、文献表格抽取、材料结构与性能关系 |
| 当前状态 | 已形成 OPV-DB 结构化数据库和较完整的字段/验证统计 |
| 负责人/参与者 | 待填写 |
| 更新时间 | 待填写 |

## 研究问题

有机光伏领域已经积累大量器件性能数据，但这些数据分散在论文、表格、补充材料和不同命名规则中，难以直接用于比较、建模和候选材料筛选。

本项目关注如何把 OPV 文献中的 donor/acceptor、器件结构、制备条件、PCE/Voc/Jsc/FF 等性能指标和材料标识符整理成统一数据库，并进一步服务于材料性能预测、benchmark 构建和材料设计。

## 研究意义

这个项目不是 panel 的生物主体方向，但它是团队数据驱动科学探索能力的一个完整案例。它展示了从大规模文献到结构化数据库、字段覆盖、质量验证和建模准备的完整过程。

在对老师展示时，可以把它放在“横向数据资源能力”部分：说明团队不仅能做生物机制问题，也能做科学文献数据结构化和模型数据集建设。

## 项目目标

- 完成 OPV-DB 的数据规模、字段结构、来源和验证说明。
- 将 donor/acceptor、SMILES、器件结构、核心性能指标和处理条件整理成可用于分析的结构化表。
- 为后续 PCE 预测、材料筛选、器件条件分析或 benchmark 建设提供数据基础。
- 准备一页简洁展示：数据规模、字段覆盖、验证结果和可用任务。

## 技术路线

1. 文献元数据采集和 DOI 归一化。
2. 处理 full text 和 tables，优先抽取含 PCE、Voc、Jsc、FF、donor、acceptor、device stack、solvent、additive、thickness、annealing 等信息的表格。
3. 建立 device-level record，而不是只记录每篇文章的最佳值。
4. 对 material names 做 canonical normalization，并映射 donor/acceptor SMILES 和能级信息。
5. 进行字段完整性、物理范围和 PCE 公式一致性验证。
6. 根据不同任务过滤记录：核心器件分析要求 PCE/Voc/Jsc/FF/donor/acceptor，分子建模还要求 donor_smiles 和 acceptor_smiles。

## 当前进展

OPV-DB 已经形成完整的数据描述和验证框架：

- 数据库包含 40599 条 device records，来自 8018 个 source DOI。
- 文献 harvest 包含 19765 条 article rows，extraction result table 包含 18874 行。
- material reference table 包含 4629 个 material records。
- 数据中有 5162 个 normalized donor labels、5491 个 normalized acceptor labels、13359 个 donor-acceptor label pairs。
- PCE 覆盖 40341 条记录，占 99.4%；PCE/Voc/Jsc/FF 四个核心指标同时覆盖 38328 条记录，占 94.4%。
- donor 和 acceptor SMILES 同时覆盖 39063 条记录，占 96.2%。
- 物理范围验证通过情况良好：PCE、Voc、Jsc、FF 均处于设定合理范围；PCE 公式重算在 5% 相对误差内的记录为 35892/38328，占 93.6%，10% 内为 37036/38328，占 96.6%。
- 当前短板主要在 processing descriptors：active-layer thickness 覆盖约 14.7%，annealing temperature 覆盖约 11.9%。

