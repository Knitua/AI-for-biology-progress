# Project Update Prompt

下次当某个项目有新进展，或需要新建项目时，可以直接把下面这段 prompt 发给 Codex，并把新文件放到对应项目文件夹中。

```text
请更新生物探索团队 panel 中 `AI-for-biology-progress` 仓库下的项目页。

工作目录：
.

路径约定：
- 当前工作目录默认为 `AI-for-biology-progress` 仓库根目录。
- 项目目录：`XXAI-项目名`
- 项目模板：`Template\Project_Template.md`
- 项目总览：`Panel_plan.md`
- 项目列表：`项目列表.md`
- 更新记录与可视化目录：`paint`
- 只使用相对路径，不要写入任何盘符绝对路径。

任务类型：
【在这里选择并填写】
1. 更新已有项目：项目文件夹为 `XXAI-项目名`
2. 新建项目：项目名称为 `AI-项目名`，需要自动分配下一个编号

本次更新目标：
【简要写这次新增了什么进展，例如：新增实验结果、补充模型结果、更新候选列表、加入新的 protocol、开辟新方向等】

请严格按以下要求执行：

1. 先定位目标项目文件夹。
   - 如果用户只给 `XXAI-项目名`，默认理解为当前仓库根目录下的项目文件夹。
   - 不要更新相邻的 `AI-for-biology-recruit` 仓库，除非用户明确要求。

2. 先检查是否真的有新文件或材料更新。
   - 读取 `paint\update_status.csv`，找到目标项目对应行。
   - 对比目标项目文件夹内材料文件的最后修改时间，以及 `update_status.csv` 中记录的 `last_scanned_at` / `latest_source_mtime`。
   - 忽略 `README.md`、临时文件、系统文件、`*.minutes.md`、`paint` 中的记录文件。
   - 如果目标项目文件夹没有新增文件，且材料文件没有晚于上次扫描时间的修改，则不要重写该项目 README，也不要为了该项目改写 `Panel_plan.md`；只在最终回复中说明“该项目无新增材料，已跳过”。
   - 如果用户明确要求“强制刷新/重写/重新整理”，才允许在无新增文件时重写。

3. 如果检测到新文件或材料更新，再完整阅读目标项目文件夹中的所有新增材料和已有 README。
   - PDF、Word、Excel、Markdown、图片说明、结果表都要尽量读取。
   - 如果有无法解析的文件，明确说明无法解析哪些文件，但不要因此跳过其他可读材料。

4. 提取项目事实，而不是罗列文件。
   - 需要总结研究问题、研究意义、项目目标、技术路线和当前进展。
   - 当前进展要写成团队已经完成的工作、得到的结果、形成的路线和需要谨慎表述的边界。
   - 不要写“当前已有 xxx.pdf”“根据某文档”“材料显示”“我阅读了”等内部整理语言。
   - 假设老师不会点开原始文件，README 本身必须能独立讲清楚项目。

5. 统一使用 `Template\Project_Template.md` 的结构。
   - 小标题只能使用：基本信息、研究问题、研究意义、项目目标、技术路线、当前进展。
   - 不要新增“参考资料”“已有材料”“一句话概括”等额外主标题。

6. 写作风格要求。
   - 语言要学术化、科学、适合给老师看。
   - 不要过度 AI 味，不要写泛泛的“AI赋能”“智能化探索”等空话。
   - 能给数字就给数字，能给阶段性结果就给结果。
   - 对未完成或证据不足的部分要谨慎表述，明确 claim boundary。

7. 如果是更新已有项目：
   - 保留项目已有结构。
   - 将新增材料转化为项目进展，不要只是追加文件名。
   - 必要时更新项目目标、技术路线和当前进展。

8. 如果是新建项目：
   - 在 `项目列表.md` 中追加编号和项目名。
   - 在当前仓库根目录下创建编号项目文件夹，例如 `11AI-项目名`。
   - 根据 `Template\Project_Template.md` 创建 `README.md`。
   - 如果新项目已有材料，先读材料后再写；如果没有材料，则明确写成“待启动方向”，但仍给出合理研究问题和下一步。

9. 同步更新 `Panel_plan.md`。
   - 更新项目总数、已有材料项目数、重点推进项目和项目进展矩阵。
   - 如果该项目适合放入“重点展示项目”，同步更新对应摘要。
   - 项目进展矩阵中的“当前进展材料”可以概括材料类型，但不要只堆文件名；优先写数据规模、实验结果、protocol 状态或可展示成果。
   - 首页摘要和重点展示项目不要写“已有某文件”，要写项目事实和阶段性结果。

10. 更新 `paint` 中的状态记录和可视化文件。
   - 更新 `paint\update_status.csv` 中该项目行的 `last_scanned_at`、`latest_source_mtime`、`last_content_update`、`update_count` 和 `notes`。
   - 如果本次跳过该项目，仍可更新 `last_scanned_at`，但不要更新 `last_content_update` 和 `update_count`。
   - 在 `paint\update_history.csv` 追加一行，记录本次是 `updated`、`skipped` 还是 `created`，并简要说明原因。
   - 运行或维护 `paint\index.html`，让它反映最新项目和会议文件更新时间。

11. 完成后请检查：
   - 所有项目 README 标题结构是否统一。
   - 是否残留 `.pdf`、`.docx`、`.xlsx`、`当前已有`、`材料显示`、`文档记录` 等内部文件表述。
   - `Panel_plan.md` 与项目 README 的状态是否一致。
   - `项目列表.md`、项目目录编号、`Panel_plan.md` 的项目总数是否一致。
   - `paint\update_status.csv` 与本次实际更新/跳过情况是否一致。
   - 所有新增或修改的路径是否都是相对路径。
```

## 快速使用版

如果只是更新一个已有项目，可以发送：

```text
请根据 `XXAI-项目名` 里新增的文件更新该项目 README，并同步更新 `Panel_plan.md`。

要求：
1. 先检查 `paint\update_status.csv` 和项目文件夹修改时间；没有新增或更新材料就跳过，不要重写 README 和 Panel_plan。
2. 如果有新材料，再读完项目文件夹里的材料，并总结项目事实。
3. README 使用 `Template\Project_Template.md` 的 6 个标题。
4. 不要写“当前已有某 PDF/文档/材料显示”，要直接写项目进展。
5. 写成老师可直接阅读的学术化项目介绍。
6. 完成后更新 `paint\update_status.csv`、`paint\update_history.csv` 和 `paint\index.html`。
7. 完成后检查 `Panel_plan.md`、`项目列表.md`、项目 README 是否一致，且路径均为相对路径。
```

## 新建项目快速版

```text
请新建一个项目：AI-项目名。

要求：
1. 在当前仓库根目录下自动分配下一个编号并创建文件夹。
2. 如果我已经放入了材料，请先读取材料再写 README。
3. README 使用 `Template\Project_Template.md` 的 6 个标题。
4. 同步更新 `项目列表.md` 和 `Panel_plan.md`。
5. 在 `paint\update_status.csv` 新增项目行，并在 `paint\update_history.csv` 记录 `created`。
6. 不要在 README 里暴露“看了哪个文件”，只展示项目事实、进展、目标和下一步。
```
