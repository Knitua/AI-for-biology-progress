# 10AI-吸附质放置

## 基本信息

| 字段 | 内容 |
|---|---|
| 项目方向 | 吸附质初始构型生成、催化表面低能吸附位点、energy-conditioned flow matching |
| 当前状态 | 已形成 AdsorbFlow 方法框架、benchmark 结果和适用边界 |
| 负责人/参与者 | 待填写 |
| 更新时间 | 2026-02-22 |

## 研究问题

异相催化计算筛选中，一个实际瓶颈是如何把吸附质放到催化表面上，使其经过后续 MLFF/DFT relaxation 后落入正确的低能吸附构型。传统枚举方法需要大量 relaxation，扩散模型虽然提升了成功率，但通常需要约 100 个反向采样步骤。

本项目关注的问题是：能否用 deterministic flow matching 在吸附质刚体平移和旋转空间中快速生成低能初始构型，并在减少采样步骤的同时保持或提升 DFT 验证成功率。

## 研究意义

吸附质放置是催化、材料和表界面计算中的前处理关键步骤。一个更快、更准的放置模型可以显著提高高通量催化筛选效率，也能成为 AI-DFT-实验闭环中的入口模块。

虽然该项目不是生物方向主体，但它与团队的分子建模、催化和科学计算能力相关，适合放在 panel 的方法拓展部分。

## 项目目标

- 理解 AdsorbFlow 的任务定义、方法和结果。
- 将吸附质放置问题表述为 translation + SO(3) rotation 的刚体构型生成任务。
- 梳理 energy-conditioned flow matching 如何替代 diffusion sampling。
- 明确该方法与 AdsorbDiff、AdsorbML 的性能差异和适用边界。
- 判断是否可以迁移到团队后续的材料、催化或生物界面建模任务中。

## 技术路线

1. 数据集：使用 OC20-Dense，每个 slab-adsorbate system 有约 100 个局部最小吸附构型和能量。
2. 构型表达：吸附质作为刚体，建模二维平面平移 `t=(tx, ty)` 和三维旋转 `R in SO(3)`；垂直高度由后续 MLFF relaxation 调整。
3. 训练目标：从 relaxed low-energy pose 到 random rigid-body placement 构造 flow matching 路径，学习时间依赖 vector field。
4. 能量条件：使用 relative energy 通过 classifier-free guidance conditioning 加入模型，而不是显式使用能量梯度。
5. 采样：从随机 placement 出发，反向积分 ODE，默认只需 5 个 generative steps。
6. 验证：生成 10 个候选，MLFF relaxation + anomaly filtering 后，用 VASP DFT single-point 验证是否在 DFT reference minimum 0.1 eV 内。

## 当前进展

AdsorbFlow 已经形成完整方法和 benchmark 结果：

- 方法上提出 energy-conditioned deterministic transport，用 conditional flow matching 替代随机扩散反向过程。
- 采样效率明显提升：默认 5 步 ODE integration，相比 diffusion baseline 约 100 步有约 20 倍步数减少。
- 在 OC20-Dense 44 个 in-distribution systems 上，EquiformerV2 backbone 的 AdsorbFlow 达到 DFT SR@1 = 34.1%、SR@10 = 61.4%。
- 对比基线：AdsorbDiff 为 SR@1 = 31.8%、SR@10 = 41.0%；AdsorbML 为 SR@10 = 47.7%。AdsorbFlow 在主要指标上更优。
- anomaly rate 方面，AdsorbFlow EquiformerV2 的 Anom.@10 为 6.8%，低于 AdsorbDiff 的 13.6%，与 AdsorbML 持平。
- 在 50 个 out-of-distribution systems 上，AdsorbFlow 保持 SR@10 = 58.0%，MLFF-to-DFT gap 约 4 个百分点。
- 已明确方法边界：当前将吸附质视为刚体，适合小到中等吸附质；对大分子内部 torsion、co-adsorbates、coverage effects、uncertainty 和闭环实验仍需扩展。

