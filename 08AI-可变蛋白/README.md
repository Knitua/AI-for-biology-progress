# 08AI-可变蛋白

## 基本信息

| 字段 | 内容 |
|---|---|
| 项目方向 | 内在无序蛋白 IDP 构象 ensemble 生成、聚合物先验、flow matching 与热力学 observable 审计 |
| 当前状态 | 已形成 ThermoProt 方法框架、本地 benchmark 结果和限制分析 |
| 负责人/参与者 | 待填写 |
| 更新时间 | 待填写 |

## 研究问题

本项目实际研究对象不是泛泛的“可变蛋白”，而是 **内在无序蛋白（IDP）的构象 ensemble 生成**。IDP 的功能不能用单一静态结构描述，更需要描述一组快速转换的构象分布。

核心问题是：能否用带有聚合物物理先验的 flow matching 模型，生成合理的 Cα 级 IDP 构象 ensemble，并用 Rg、contact map、RMSF、chemical shift 等 observable 审计模型的成功和失败。

## 研究意义

许多蛋白尤其是 IDP 并不存在唯一稳定构象，传统单结构预测无法完整表达其功能状态。这个项目的意义在于把蛋白 ensemble 问题和热力学/聚合物物理联系起来：不是只生成“看起来像”的结构，而是检查生成分布是否在全局尺寸、接触概率、柔性和实验 observable 上合理。

对团队展示来说，这个项目很适合作为“蛋白构象生成 + 物理约束 + 谨慎 benchmark 审计”的代表，亮点是边界讲得很清楚：当前可以说是一个 thermodynamically motivated Cα ensemble generator，但不能说已经是严格平衡模拟器或 broad SOTA。

## 项目目标

- 将 ThermoProt 定位为 Cα 级 IDP ensemble generator。
- 使用 Gaussian、freely-jointed-chain 和 Flory-inspired polymer priors 作为生成源分布。
- 通过 optimal-transport conditional flow matching 学习从聚合物先验到数据来源 IDP ensemble 的 transport。
- 用等变几何网络处理序列条件和空间结构。
- 用多层次 observable 评估生成 ensemble，而不是只看单一结构误差。

## 技术路线

1. 输入蛋白序列，使用 amino-acid embedding 和可选 ESM-2 embedding 表征序列。
2. 从 Gaussian/FJC/Flory-inspired Cα polymer prior 采样初始链构象。
3. 使用 conditional flow matching 训练 velocity model，将 source samples 传输到目标 ensemble。
4. 模型架构 GeoFormer 结合 Invariant Point Attention、E(n)-equivariant graph updates、time-conditioned normalization 和 pair-distance features。
5. 采样阶段通过 Euler、RK4 等 ODE solver 生成构象 ensemble，并可使用 classifier-free guidance。
6. 评估阶段计算 Rg、contact probability、RMSF correlation、PCA-W2、chemical shift 等 observable。

## 当前进展

ThermoProt 已经形成完整的方法框架、结果审计、限制分析和后续计划：

- 已明确 ThermoProt 的定位：带聚合物先验的 Cα 级 IDP ensemble generator，不是分子动力学 force field，也不显式学习 PMF 或 partition function。
- 已完成主要方法描述：使用 optimal-transport conditional flow matching 和等变几何网络，从 Gaussian/FJC/Flory prior 生成 IDP ensemble。
- 已完成本地 benchmark 审计，结果支持“局部 protocol 下的 ensemble 生成能力”，但不支持 broad SOTA 叙述。
- IDRome20 matched comparison 中，ThermoProt 在 Rg MAE、contact Jaccard、Rg Pearson r 等指标上与 STARLING 可比或更优；例如 nconf=100 时 Rg MAE 约 1.445、contact Jaccard 约 0.862、Rg Pearson r 约 0.968。
- IDPForge S1 和 CALV ADOS3 的 Rg-centered rerun 显示，模型能在部分 benchmark 上达到约 5-7% 的 Rg 误差水平；CALV ADOS3 nconf=100 时 Rg MAE 约 1.93 Å、Rg r 约 0.980。
- PED 和 NMR chemical-shift 结果仍然混合：PED 上不同 protocol 存在 compactness/shape tradeoff；NMR clean/confounded split 改变结论，不能支持全局 NMR 成功声明。
- 已整理 SOTA-readiness gap：缺少完全匹配 baseline、SAXS/FRET/PRE/RDC 等实验闭环、热力学校准、环境条件响应、all-atom refinement 和长 IDR scaling/speed 证据。
- 已提出后续热力学扩展方向：polymer scaling diagnostics、maximum-entropy reweighting、condition dependence、sparse/low-rank long-IDR architecture。

