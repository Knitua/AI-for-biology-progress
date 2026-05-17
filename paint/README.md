# 更新记录与可视化

这个目录用于记录 `To teacher` 视图下项目文件夹和会议文件的更新时间。

## 文件说明

- `update_status.csv`：每个项目文件夹和会议总结 `.minutes.md` 的当前状态；不记录原始会议转写 `.txt`。
- `update_history.csv`：每次更新、跳过或初始化的历史记录。
- `index.html`：可直接打开的可视化页面。
- `refresh_paint.py`：扫描 `To teacher` 并刷新状态表和可视化页面。

## 使用

从 Panel 根目录运行：

```powershell
python "To teacher\paint\refresh_paint.py"
```

更新项目时的规则：

- 如果某个项目没有新增或修改过的材料，不重写该项目 README，也不因为它改写 `Panel_plan.md`。
- 如果项目有新材料，更新项目 README、`Panel_plan.md`，并同步更新本目录的状态和历史记录。
- 会议记录只维护 `.minutes.md` 的更新时间；原始 `.txt` 作为输入材料保留在 `Meet_content` 中，不进入状态表。
