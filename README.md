# Bio Panel Teacher View

## 时间戳与更新面板

请优先打开下面的页面查看项目和会议总结的更新时间：

### [打开项目进展更新时间面板](https://knitua.github.io/AI-for-biology-progress/)

本地查看：

### [打开本地更新时间面板](./paint/index.html)

刷新时间戳数据：

```powershell
python "paint\refresh_paint.py"
```

时间戳数据文件：

- [update_status.csv](./paint/update_status.csv)：当前项目和会议总结的最后更新时间。
- [update_history.csv](./paint/update_history.csv)：每次更新、跳过或初始化的记录。

---

## 每次怎么更新

### 更新已有项目

1. 把新材料放入对应项目文件夹，例如 `05AI-级联催化逆合成`。
2. 使用 [Project_Prompt.md](./Update_prompt/Project_Prompt.md) 中的项目更新 prompt。
3. 更新完成后刷新时间戳面板：

```powershell
python "paint\refresh_paint.py"
```

规则：

- 没有新增或修改材料的项目不需要重写。
- 有新材料的项目才更新 `README.md` 和 [Panel_plan.md](./Panel_plan.md)。
- 项目页统一使用 [Project_Template.md](./Template/Project_Template.md) 的结构。

### 新建项目

1. 把材料放入 `AI-for-biology-progress` 下的新项目文件夹，或先准备项目名称。
2. 使用 [Project_Prompt.md](./Update_prompt/Project_Prompt.md) 的“新建项目快速版”。
3. 同步检查：
   - [项目列表.md](./项目列表.md)
   - [Panel_plan.md](./Panel_plan.md)
   - 新项目 `README.md`
   - [更新时间面板](./paint/index.html)

### 生成会议总结

1. 把会议转写稿放入 `Meet_content`。
2. 使用 [Meeting_Minutes_Agent_Prompt.md](./Update_prompt/Meeting_Minutes_Agent_Prompt.md)。
3. 生成的会议总结保存为 `YYYY-MM-DD-主题.minutes.md`。
4. 只在更新时间面板中维护 `.minutes.md`，不记录原始 `.txt`。

---

## 快速入口

- [项目总览](./Panel_plan.md)
- [项目列表](./项目列表.md)
- [更新时间面板](https://knitua.github.io/AI-for-biology-progress/)
- [本地更新时间面板](./paint/index.html)
- [项目更新 Prompt](./Update_prompt/Project_Prompt.md)
- [会议总结 Prompt](./Update_prompt/Meeting_Minutes_Agent_Prompt.md)
- [项目模板](./Template/Project_Template.md)
