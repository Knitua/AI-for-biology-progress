# 更新记录与可视化

这个目录用于记录 `AI-for-biology-progress` 视图下项目文件夹和会议总结的更新时间。

## 文件说明

- `update_status.csv`：每个项目文件夹和会议总结 `.minutes.md` 的当前状态；不记录原始会议转写 `.txt`。
- `update_history.csv`：每次更新、跳过或初始化的历史记录。
- `project_meta.csv`：项目卡片、项目分类、关键数字、下一步和边界的元信息数据源。
- `project_events.csv`：首页总日历、会议日历和项目详情页底部子日历的数据源；增删会议和里程碑时维护这个文件。
- `index.html`：项目进展总览。
- `projects.html`：项目进展列表。
- `project-XX.html`：由各项目 `README.md` 生成的项目详情页。
- `meetings.html`：会议记录页。
- `updates.html`：项目与会议文件更新时间页。
- `styles.css`：统一样式。
- `refresh_paint.py`：扫描当前仓库并刷新状态表和静态页面。

## 项目日历

`project_events.csv` 的每一行是一条会议或里程碑：

- `event_id`：唯一 ID，会生成项目页锚点。
- `project_id`：项目文件夹名，例如 `05AI-级联催化逆合成`。
- `date`：节点日期，格式 `YYYY-MM-DD`。
- `event_type`：`meeting` 或 `milestone`。
- `status`：`done` 或 `planned`。
- `title` / `summary`：节点标题和说明。
- `source_path`：可选，指向会议纪要或项目 README。

新增或删除项目时，项目页会按目录自动生成；如需在总日历和项目底部子日历出现对应节点，同步增删 `project_events.csv` 中对应 `project_id` 的记录。项目页子日历会自动过滤出当前项目记录。

## 项目增删

- 新增项目：创建 `XXAI-项目名/README.md`，再在 `project_meta.csv` 中增加同名 `project_id` 行。
- 删除项目：删除项目目录，并删除 `project_meta.csv` 与 `project_events.csv` 中对应 `project_id` 的行。
- 如果只创建项目目录但不补 `project_meta.csv`，页面仍会生成项目详情，但项目卡片会使用默认文案。

## 使用

从 Panel 根目录运行：

```powershell
python "paint\refresh_paint.py"
```

更新项目时的规则：

- 如果某个项目没有新增或修改过的材料，不重写该项目 README，也不因为它改写 `Panel_plan.md`。
- 如果项目有新材料，更新项目 README、`Panel_plan.md`，并同步更新本目录的状态和历史记录。
- 会议记录只维护 `.minutes.md` 的更新时间；原始 `.txt` 作为输入材料保留在 `Meet_content` 中，不进入状态表。
