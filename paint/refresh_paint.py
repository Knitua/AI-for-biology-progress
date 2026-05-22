import csv
import calendar
import hashlib
import html
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


PAINT_DIR = Path(__file__).resolve().parent
TEACHER_DIR = PAINT_DIR.parent
STATUS_PATH = PAINT_DIR / "update_status.csv"
HISTORY_PATH = PAINT_DIR / "update_history.csv"
META_PATH = PAINT_DIR / "project_meta.csv"
EVENTS_PATH = PAINT_DIR / "project_events.csv"
HTML_PATH = PAINT_DIR / "index.html"
CSS_PATH = PAINT_DIR / "styles.css"

STATUS_FIELDS = [
    "item_type",
    "item_name",
    "relative_path",
    "last_scanned_at",
    "latest_source_mtime",
    "last_content_update",
    "update_count",
    "needs_update",
    "notes",
]

HISTORY_FIELDS = [
    "event_time",
    "item_type",
    "item_name",
    "relative_path",
    "action",
    "summary",
]

IGNORE_PROJECT_FILES = {
    "README.md",
}

PROJECT_META = {
    "01AI-BAT": {
        "tier": "重点项目",
        "maturity": "模型/计算推进中",
        "domain": "蝙蝠免疫与病毒耐受",
        "summary": "从 Bat1K 和比较基因组资源中筛选免疫、病毒耐受、炎症调控和 DNA 修复相关候选基因，适合作为生物机制探索主线。",
        "key_numbers": ["1469 个物种状态条目", "91 个完成测序/组装/注释", "第一版 ESM2 试点路线"],
        "next_step": "收敛 10-20 个试点物种与候选免疫基因清单，跑通 protein/CDS 表征和可视化。",
        "risk": "不要从 TB 级原始 reads 起步；先用已注释 genome/CDS/protein 数据做小规模试点。",
    },
    "02AI-老药新用": {
        "tier": "重点项目",
        "maturity": "阶段性成果已形成",
        "domain": "癌症相关 drug-target pair 筛选",
        "summary": "已完成 FDA 小分子与人类蛋白靶点的大规模筛选，并形成疾病证据整合和结构增强结果。",
        "key_numbers": ["915000 个 pair", "Top1000 结构增强", "940 个 DiffDock 有效输出"],
        "next_step": "从 Stage 6 Top100 中按癌种、机制证据和实验可行性下选 20-50 个候选。",
        "risk": "Full DiffDock 尚未完成，磁盘和失败任务重跑策略需要先解决。",
    },
    "03AI-LNP": {
        "tier": "待启动/支撑方向",
        "maturity": "任务定义待补齐",
        "domain": "脂质纳米颗粒递送系统",
        "summary": "方向已建立，但第一阶段应用场景、变量体系和可用数据源仍需收敛。",
        "key_numbers": ["应用场景待定", "关键变量待整理", "无新增结果材料"],
        "next_step": "确定 mRNA、siRNA、肝靶向或通用配方整理中的一个最小任务。",
        "risk": "若不先确定应用场景，项目容易停留在泛泛的递送系统介绍。",
    },
    "04AI-生物化学": {
        "tier": "待启动/支撑方向",
        "maturity": "知识底座待定义",
        "domain": "团队共用机制框架",
        "summary": "更适合作为团队生物化学基础支撑页，帮助不同项目共享蛋白、药物、代谢、通路等概念语言。",
        "key_numbers": ["支撑 10 个方向", "可转知识库", "内容框架待明确"],
        "next_step": "决定做知识库、课程式内容，还是某个具体生物化学研究问题。",
        "risk": "不能只做概念堆叠，需要绑定到团队项目里的真实机制问题。",
    },
    "05AI-级联催化逆合成": {
        "tier": "数据资源能力",
        "maturity": "数据资源成型",
        "domain": "级联反应结构化数据库",
        "summary": "已形成 Cascade Dataset v4 和质量分层体系，支撑复杂文献知识结构化与后续路线评估任务。",
        "key_numbers": ["3810 条 reaction records", "8609 个 steps", "3744 条 gold/silver release"],
        "next_step": "优先做路线级级联可行性评估，而不是从零训练完整规划模型。",
        "risk": "现有数据量不足以支撑强生成式级联规划，短期应聚焦评估器和路线修饰。",
    },
    "06AI-有机光伏材料": {
        "tier": "数据资源能力",
        "maturity": "数据资源成型",
        "domain": "OPV 文献数据库与材料性能",
        "summary": "OPV-DB 已完成从文献表格到 device-level 数据库、字段覆盖和物理验证的数据资源建设。",
        "key_numbers": ["40599 条 device records", "8018 个 DOI", "94.4% 核心指标完整"],
        "next_step": "确定第一阶段主任务：数据集建设、PCE 预测、材料筛选或器件条件分析。",
        "risk": "处理条件字段覆盖较弱，厚度和退火温度仍需补齐或明确边界。",
    },
    "07AI-抗冻肽": {
        "tier": "重点项目",
        "maturity": "结果推进中",
        "domain": "抗冻蛋白/肽预测生成与实验验证",
        "summary": "已经形成预测、生成、天然库筛选、motif 挖掘和湿实验验证的完整路线。",
        "key_numbers": ["64 万极地蛋白初筛", "约 8000 条 AFP-like 生成候选", "815/1000 LoRA 命中率"],
        "next_step": "从候选蛋白 motif 下切到短肽，并补齐冰重结晶抑制和结构表征结果。",
        "risk": "抗冻肽直接数据稀缺，需要谨慎区分 AFP-like 蛋白命中和短肽功能验证。",
    },
    "08AI-可变蛋白": {
        "tier": "重点项目",
        "maturity": "方法框架成型",
        "domain": "IDP ensemble 生成",
        "summary": "ThermoProt 已形成聚合物先验、flow matching、等变网络和 observable 审计框架。",
        "key_numbers": ["Rg Pearson r 约 0.968", "contact Jaccard 约 0.862", "5-7% Rg 误差水平"],
        "next_step": "补齐匹配 baseline、SAXS/FRET/PRE 等实验闭环和热力学校准证据。",
        "risk": "只能表述为 Cα 级 IDP ensemble generator，不能宣称严格平衡模拟器或 broad SOTA。",
    },
    "09AI-胃癌预测": {
        "tier": "重点项目",
        "maturity": "任务细化中",
        "domain": "胃癌免疫治疗响应预测",
        "summary": "围绕多模态数据、概念瓶颈和 TLS 弱监督识别，目标是输出临床可解释的响应预测报告。",
        "key_numbers": ["约 29 例小样本", "4 张标注 WSI", "TLS patch-level 热图路线"],
        "next_step": "规范 TLS 点标注到 patch 标签的生成策略，并连接 TLS 热图与响应预测主线。",
        "risk": "样本量小且标注为点标注，模型结论需要强调弱监督和质量控制边界。",
    },
    "10AI-吸附质放置": {
        "tier": "方法拓展",
        "maturity": "方法调研/复现评估",
        "domain": "催化表面吸附构型生成",
        "summary": "AdsorbFlow 代表 flow matching 在材料/催化界面建模中的方法扩展方向。",
        "key_numbers": ["5 步 ODE 采样", "SR@10 = 61.4%", "约 20 倍采样步数减少"],
        "next_step": "判断能否迁移到团队后续材料、催化或生物界面建模任务。",
        "risk": "当前为刚体吸附质放置；大分子 torsion、co-adsorbates 和不确定性仍未覆盖。",
    },
}

STYLE_CSS = """
:root {
  --bg: #f5f6f8;
  --panel: #ffffff;
  --ink: #16202a;
  --muted: #5f6b78;
  --line: #dce2e8;
  --line-strong: #c7d0d9;
  --teal: #23676f;
  --blue: #315f9f;
  --copper: #916331;
  --green: #247044;
  --red: #a23a30;
  --amber-bg: #fff4df;
  --green-bg: #e8f4ec;
  --red-bg: #ffe8e5;
  --blue-bg: #eaf0fb;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: var(--ink);
  background: var(--bg);
  font-family: Arial, "Microsoft YaHei", "PingFang SC", sans-serif;
  line-height: 1.58;
}

a {
  color: #225c76;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.site-header {
  border-bottom: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.96);
}

.header-inner {
  max-width: 1220px;
  margin: 0 auto;
  padding: 14px 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.brand {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand strong {
  font-size: 15px;
  letter-spacing: 0;
}

.brand span {
  color: var(--muted);
  font-size: 12px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.nav a {
  color: #33404d;
  border-radius: 6px;
  padding: 7px 10px;
  font-size: 14px;
}

.nav a.active {
  color: #ffffff;
  background: var(--teal);
}

main {
  max-width: 1220px;
  margin: 0 auto;
  padding: 28px 22px 52px;
}

.hero {
  padding: 14px 0 26px;
  border-bottom: 1px solid var(--line);
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--teal);
  font-size: 13px;
  font-weight: 700;
}

h1 {
  margin: 0;
  max-width: 900px;
  font-size: clamp(28px, 4vw, 46px);
  line-height: 1.12;
  letter-spacing: 0;
}

.lede {
  max-width: 920px;
  margin: 14px 0 0;
  color: #465360;
  font-size: 17px;
}

.meta-line {
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
}

.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.calendar-panel {
  margin-top: 22px;
  padding: 18px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 10px 28px rgba(34, 48, 62, 0.06);
}

.calendar-disclosure {
  padding: 0;
  overflow: hidden;
}

.calendar-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 16px 18px;
  cursor: pointer;
  list-style: none;
}

.calendar-toggle::-webkit-details-marker {
  display: none;
}

.calendar-toggle-title {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.calendar-toggle-title strong {
  color: #182633;
  font-size: 20px;
  line-height: 1.25;
}

.calendar-toggle-title span {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.4;
}

.calendar-toggle-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
  color: #33404d;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 10px;
  background: #fbfcfd;
  font-size: 12px;
  font-weight: 800;
}

.calendar-toggle-action::after {
  content: "+";
  display: inline-grid;
  place-items: center;
  width: 18px;
  height: 18px;
  color: #ffffff;
  border-radius: 999px;
  background: var(--teal);
  line-height: 1;
}

.calendar-disclosure[open] .calendar-toggle {
  border-bottom: 1px solid var(--line);
}

.calendar-disclosure[open] .calendar-toggle-action::after {
  content: "-";
}

.calendar-body {
  padding: 16px 18px 18px;
}

.calendar-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}

.calendar-head h2 {
  margin: 0;
  font-size: 20px;
}

.calendar-head p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.calendar-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.calendar-summary-item {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfd;
}

.calendar-summary-item strong {
  color: #182633;
  font-size: 18px;
  line-height: 1.2;
}

.calendar-summary-item span {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.35;
}

.calendar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--teal);
}

.legend-dot.meeting {
  background: var(--blue);
}

.legend-dot.done {
  background: var(--green);
}

.legend-dot.planned {
  background: var(--copper);
}

.calendar-months {
  display: grid;
  gap: 16px;
}

.calendar-month {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
}

.calendar-month-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  background: #eef2f4;
}

.calendar-month-title h3 {
  margin: 0;
  font-size: 16px;
}

.calendar-month-title span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}

.calendar-weekday {
  padding: 8px 10px;
  color: var(--muted);
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: #f7f9fa;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.calendar-weekday:nth-child(7) {
  border-right: 0;
}

.calendar-day {
  position: relative;
  min-height: 132px;
  padding: 8px;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: #ffffff;
  transition: background 160ms ease;
}

.calendar-day:nth-child(7n) {
  border-right: 0;
}

.calendar-day.empty {
  background: #f3f5f7;
}

.calendar-day.no-events {
  background: #fbfcfd;
}

.calendar-day.has-events {
  background: linear-gradient(180deg, #ffffff 0%, #fbfcfd 100%);
}

.calendar-day.today {
  outline: 2px solid rgba(35, 103, 111, 0.32);
  outline-offset: -2px;
}

.calendar-day:hover {
  background: #f7fafb;
}

.calendar-date {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  color: #2f3b46;
  font-size: 13px;
  font-weight: 800;
}

.calendar-date span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.calendar-events {
  display: grid;
  gap: 5px;
  margin-top: 8px;
}

.calendar-day-more {
  margin-top: 2px;
}

.calendar-day-more summary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  color: #33404d;
  border: 1px dashed var(--line-strong);
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
  list-style: none;
}

.calendar-day-more summary::-webkit-details-marker {
  display: none;
}

.calendar-day-more summary:hover,
.calendar-day-more summary:focus-visible {
  border-color: #9fb2c2;
  text-decoration: none;
}

.calendar-day-more[open] summary {
  margin-bottom: 5px;
  color: #ffffff;
  border-color: var(--teal);
  background: var(--teal);
}

.calendar-overflow-events {
  display: grid;
  gap: 5px;
}

.calendar-event {
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr);
  gap: 6px;
  align-items: start;
  padding: 6px 7px;
  color: #22313f;
  background: #eef7f4;
  border: 1px solid #cbe4dc;
  border-radius: 6px;
}

.calendar-event::before {
  content: "";
  width: 8px;
  height: 8px;
  margin-top: 5px;
  border-radius: 999px;
  background: var(--teal);
}

.calendar-event:hover,
.calendar-event:focus-visible {
  border-color: #9fb2c2;
  box-shadow: 0 8px 18px rgba(36, 52, 67, 0.08);
  text-decoration: none;
}

.calendar-event.milestone.done {
  background: #edf7ef;
  border-color: #cde8d5;
}

.calendar-event.milestone.done::before {
  background: var(--green);
}

.calendar-event.meeting.done {
  background: #edf3fb;
  border-color: #cbdcf1;
}

.calendar-event.meeting.done::before {
  background: var(--blue);
}

.calendar-event.planned {
  background: #fff7e8;
  border-color: #ead6ad;
}

.calendar-event.planned::before {
  background: var(--copper);
}

.calendar-event-content {
  display: grid;
  gap: 1px;
  min-width: 0;
}

.calendar-event-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.project-pill {
  display: inline-flex;
  align-items: center;
  min-height: 16px;
  border: 1px solid #d5dde4;
  border-radius: 4px;
  padding: 0 4px;
  color: #31404d;
  background: #ffffff;
  font-size: 10px;
  line-height: 1.3;
}

.calendar-event.project-p01 .project-pill {
  color: #135a63;
  background: #e5f4f2;
  border-color: #b8dcd7;
}

.calendar-event.project-p02 .project-pill {
  color: #6b4a13;
  background: #fff2d2;
  border-color: #ebd098;
}

.calendar-event.project-p03 .project-pill {
  color: #3f5d18;
  background: #edf5dc;
  border-color: #cbdca1;
}

.calendar-event.project-p04 .project-pill {
  color: #55512b;
  background: #f5f1d8;
  border-color: #dcd2a1;
}

.calendar-event.project-p05 .project-pill {
  color: #78422e;
  background: #fde9de;
  border-color: #efc5b3;
}

.calendar-event.project-p06 .project-pill {
  color: #7a3d17;
  background: #fcebdd;
  border-color: #edc5a7;
}

.calendar-event.project-p07 .project-pill {
  color: #31548d;
  background: #e8f0fc;
  border-color: #bfd0ed;
}

.calendar-event.project-p08 .project-pill {
  color: #25613b;
  background: #e7f4eb;
  border-color: #bee0ca;
}

.calendar-event.project-p09 .project-pill {
  color: #74305b;
  background: #fae8f2;
  border-color: #eac0d6;
}

.calendar-event.project-p10 .project-pill {
  color: #44515e;
  background: #edf0f4;
  border-color: #ccd5df;
}

.calendar-event strong {
  font-size: 12px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.calendar-event .event-project-title {
  display: none;
  color: #52606d;
  font-size: 11px;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.compact-calendar .calendar-day {
  min-height: 102px;
}

.compact-calendar .calendar-summary {
  grid-template-columns: repeat(4, minmax(120px, 1fr));
}

.compact-calendar .calendar-months {
  gap: 12px;
}

.compact-calendar .calendar-event strong {
  font-size: 11px;
}

.event-sections {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.event-group {
  display: grid;
  align-content: start;
  gap: 10px;
}

.event-group h3 {
  margin: 0;
  font-size: 16px;
}

.event-card {
  border: 1px solid var(--line);
  border-left: 4px solid var(--teal);
  border-radius: 8px;
  padding: 12px;
  background: #fbfcfd;
}

.event-card.planned {
  border-left-color: var(--copper);
}

.event-card.milestone.done {
  border-left-color: var(--green);
}

.event-card.meeting.done {
  border-left-color: var(--blue);
}

.event-card h4 {
  margin: 4px 0 6px;
  font-size: 15px;
}

.event-card p {
  margin: 6px 0;
  color: #44515e;
  font-size: 13px;
}

.event-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.event-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
  font-size: 13px;
}

.metric-card,
.project-card,
.insight-card,
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.metric-card {
  padding: 14px 16px;
}

.metric-label {
  color: var(--muted);
  font-size: 13px;
}

.metric-value {
  margin-top: 4px;
  font-size: 30px;
  line-height: 1;
  font-weight: 800;
}

.section {
  margin-top: 30px;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.section-head h2,
.page-title h2 {
  margin: 0;
  font-size: 21px;
}

.section-head p,
.page-title p {
  margin: 4px 0 0;
  color: var(--muted);
}

.text-link {
  font-weight: 700;
  white-space: nowrap;
}

.judgement-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 12px;
}

.insight-card {
  padding: 16px;
}

.insight-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.insight-card p {
  margin: 0;
  color: #4b5865;
  font-size: 14px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(240px, 1fr));
  gap: 12px;
}

.project-card {
  position: relative;
  display: flex;
  min-height: 100%;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.project-card:hover,
.project-card:focus-within {
  border-color: #9fb2c2;
  box-shadow: 0 10px 24px rgba(36, 52, 67, 0.08);
  transform: translateY(-2px);
}

.project-card-link {
  position: absolute;
  inset: 0;
  z-index: 3;
  border-radius: 8px;
}

.project-card-link:focus-visible {
  outline: 3px solid rgba(35, 103, 111, 0.35);
  outline-offset: 3px;
}

.project-card h3,
.project-card p,
.project-card ul,
.project-card .card-topline,
.project-card .card-foot {
  position: relative;
}

.project-card h3 {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
  color: #17212b;
}

.project-card:hover h3,
.project-card:focus-within h3 {
  color: var(--teal);
}

.project-card p {
  margin: 0;
  color: #44515e;
  font-size: 14px;
}

.card-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 12px;
  line-height: 1.4;
  font-weight: 700;
  white-space: normal;
}

.badge.teal {
  color: #ffffff;
  background: var(--teal);
}

.badge.blue {
  color: #244d85;
  background: var(--blue-bg);
}

.badge.green {
  color: var(--green);
  background: var(--green-bg);
}

.badge.red {
  color: var(--red);
  background: var(--red-bg);
}

.badge.amber {
  color: #7b551b;
  background: var(--amber-bg);
}

.number-list,
.action-list,
.plain-list {
  margin: 0;
  padding-left: 18px;
}

.number-list li,
.action-list li,
.plain-list li {
  margin: 5px 0;
}

.stat-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.stat-list li {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 4px 7px;
  color: #44515e;
  background: #fbfcfd;
  font-size: 12px;
}

.card-foot {
  margin-top: auto;
  display: grid;
  gap: 8px;
  border-top: 1px solid var(--line);
  padding-top: 11px;
  font-size: 13px;
}

.card-foot span {
  color: var(--muted);
  font-weight: 700;
}

.two-col {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(260px, 0.9fr);
  gap: 18px;
  align-items: start;
}

.panel {
  padding: 18px;
}

.panel h2,
.panel h3 {
  margin-top: 0;
}

.project-detail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  align-items: start;
}

.content-stack {
  display: grid;
  gap: 14px;
}

.md-section {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 20px;
}

.md-section h2,
.md-section h3 {
  margin-top: 0;
}

.md-section p {
  margin: 10px 0;
}

.side-panel {
  position: sticky;
  top: 12px;
  display: grid;
  gap: 12px;
}

.fact-row {
  display: grid;
  gap: 4px;
  border-bottom: 1px solid var(--line);
  padding: 0 0 10px;
}

.fact-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.fact-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.fact-value {
  color: #2a3540;
  font-size: 14px;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}

table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--line);
  padding: 10px 12px;
  vertical-align: top;
  text-align: left;
  font-size: 13px;
}

th {
  color: #3f4b57;
  background: #eef1f4;
  font-weight: 700;
}

tr:last-child td {
  border-bottom: 0;
}

code {
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 0.95em;
}

.meeting-grid {
  display: grid;
  gap: 16px;
}

.meeting-dashboard {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.meeting-brief-grid,
.action-board {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.meeting-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
}

.meeting-brief-card {
  display: grid;
  gap: 12px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
}

.meeting-brief-card h3 {
  margin: 0;
  font-size: 18px;
  line-height: 1.35;
}

.meeting-brief-card p {
  margin: 0;
  color: #455361;
  font-size: 13px;
}

.meeting-tagline,
.meeting-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.meeting-node-card {
  border-left: 4px solid var(--blue);
}

.meeting-node-card.planned {
  border-left-color: var(--copper);
}

.meeting-link-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: auto;
  font-size: 13px;
}

.meeting-detail {
  padding: 0;
  overflow: hidden;
}

.meeting-detail summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 18px;
  cursor: pointer;
  list-style: none;
}

.meeting-detail summary::-webkit-details-marker {
  display: none;
}

.meeting-detail summary::after {
  content: "+";
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  width: 24px;
  height: 24px;
  color: #ffffff;
  border-radius: 999px;
  background: var(--teal);
  font-weight: 800;
}

.meeting-detail[open] summary {
  border-bottom: 1px solid var(--line);
}

.meeting-detail[open] summary::after {
  content: "-";
}

.meeting-detail-body {
  padding: 16px 18px 18px;
}

.meeting-card h2 {
  margin: 0 0 8px;
  font-size: 20px;
}

.meeting-columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
}

.meeting-mini-list {
  margin: 0;
  padding-left: 18px;
}

.meeting-mini-list li {
  margin: 6px 0;
  color: #394754;
  font-size: 13px;
}

.action-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
}

.action-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.update-dashboard {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.sync-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(240px, 1fr));
  gap: 12px;
}

.meeting-sync-grid {
  grid-template-columns: repeat(2, minmax(260px, 1fr));
}

.sync-card {
  display: grid;
  gap: 13px;
  min-height: 100%;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
}

.sync-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.sync-card-head h3 {
  margin: 4px 0 0;
  font-size: 17px;
  line-height: 1.35;
}

.sync-type {
  color: var(--teal);
  font-size: 12px;
  font-weight: 800;
}

.time-pair {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.time-item {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px 10px;
  background: #fbfcfd;
}

.time-item span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.time-item strong {
  display: block;
  margin-top: 3px;
  color: #182633;
  font-size: 13px;
  line-height: 1.35;
}

.sync-note {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
}

.activity-feed {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.activity-item {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 11px 12px;
  background: var(--panel);
}

.activity-time {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.activity-title {
  min-width: 0;
}

.activity-title strong {
  display: block;
  color: #182633;
  line-height: 1.35;
}

.activity-title span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}

.empty {
  color: var(--muted);
  background: var(--panel);
  border: 1px dashed var(--line-strong);
  border-radius: 8px;
  padding: 18px;
}

@media (max-width: 980px) {
  .stat-strip,
  .judgement-grid,
  .project-grid,
  .meeting-dashboard,
  .update-dashboard,
  .meeting-brief-grid,
  .action-board,
  .sync-grid,
  .meeting-sync-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .calendar-summary,
  .compact-calendar .calendar-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .event-sections {
    grid-template-columns: 1fr;
  }

  .calendar-grid {
    grid-template-columns: 1fr;
  }

  .calendar-weekday,
  .calendar-day.empty,
  .calendar-day.no-events {
    display: none;
  }

  .calendar-day {
    min-height: 0;
    border-right: 0;
  }

  .compact-calendar .calendar-day {
    min-height: 0;
  }

  .calendar-event .event-project-title {
    display: block;
  }

  .two-col,
  .project-detail,
  .meeting-columns {
    grid-template-columns: 1fr;
  }

  .activity-item {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .side-panel {
    position: static;
  }
}

@media (max-width: 640px) {
  .header-inner {
    align-items: flex-start;
    flex-direction: column;
  }

  main {
    padding: 22px 14px 42px;
  }

  .stat-strip,
  .judgement-grid,
  .project-grid,
  .calendar-summary,
  .compact-calendar .calendar-summary,
  .meeting-dashboard,
  .update-dashboard,
  .meeting-brief-grid,
  .action-board,
  .sync-grid,
  .meeting-sync-grid,
  .time-pair {
    grid-template-columns: 1fr;
  }

  .calendar-head {
    flex-direction: column;
    gap: 6px;
  }

  .calendar-toggle,
  .meeting-detail summary {
    align-items: flex-start;
    flex-direction: column;
  }

  .calendar-toggle-action {
    align-self: flex-start;
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }

  h1 {
    font-size: 30px;
  }
}
""".strip()


def rel(path: Path) -> str:
    return str(path.relative_to(TEACHER_DIR)).replace("/", "\\")


def repo_href(relative_path: str) -> str:
    return "../" + quote(relative_path.replace("\\", "/"), safe="/.-_")


def iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalize_relative_path(path_text: str) -> str:
    legacy_prefix = "To " + "teacher\\"
    for prefix in (legacy_prefix, "AI-for-biology-progress\\"):
        if path_text.startswith(prefix):
            return path_text[len(prefix) :]
    return path_text


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def clean_generated_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def write_generated(path: Path, text: str) -> None:
    path.write_text(clean_generated_text(text), encoding="utf-8")


def latest_project_source_mtime(project_dir: Path) -> str:
    timestamps: list[float] = []
    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name in IGNORE_PROJECT_FILES:
            continue
        if path.name.startswith("~$"):
            continue
        timestamps.append(path.stat().st_mtime)
    if not timestamps:
        return ""
    return iso_from_timestamp(max(timestamps))


def project_rows(existing: dict[str, dict[str, str]], now: str) -> list[dict[str, str]]:
    rows = []
    for project_dir in sorted(p for p in TEACHER_DIR.iterdir() if p.is_dir() and "AI-" in p.name[:6]):
        path_text = rel(project_dir)
        old = existing.get(path_text, {})
        readme_path = project_dir / "README.md"
        latest_source = latest_project_source_mtime(project_dir)
        if readme_path.exists():
            fallback_content_update = iso_from_timestamp(readme_path.stat().st_mtime)
        else:
            fallback_content_update = now
        old_content_update = old.get("last_content_update") or ""
        last_content_update = max(old_content_update, fallback_content_update)
        old_scan = old.get("last_scanned_at") or ""
        needs_update = "yes" if old_scan and latest_source and latest_source > old_scan else "no"
        rows.append(
            {
                "item_type": "project",
                "item_name": project_dir.name,
                "relative_path": path_text,
                "last_scanned_at": now,
                "latest_source_mtime": latest_source,
                "last_content_update": last_content_update,
                "update_count": old.get("update_count") or "0",
                "needs_update": needs_update,
                "notes": old.get("notes") or "baseline scan",
            }
        )
    return rows


def meeting_rows(existing: dict[str, dict[str, str]], now: str) -> list[dict[str, str]]:
    meet_dir = TEACHER_DIR / "Meet_content"
    if not meet_dir.exists():
        return []

    rows = []
    for path in sorted(meet_dir.glob("*.minutes.md")):
        if not path.is_file():
            continue
        path_text = rel(path)
        old = existing.get(path_text, {})
        mtime = iso_from_timestamp(path.stat().st_mtime)
        rows.append(
            {
                "item_type": "meeting_minutes",
                "item_name": path.name,
                "relative_path": path_text,
                "last_scanned_at": now,
                "latest_source_mtime": mtime,
                "last_content_update": old.get("last_content_update") or mtime,
                "update_count": old.get("update_count") or "0",
                "needs_update": "no",
                "notes": old.get("notes") or "baseline scan",
            }
        )
    return rows


def ensure_history(rows: list[dict[str, str]], status_rows: list[dict[str, str]], now: str) -> list[dict[str, str]]:
    if rows:
        return rows
    return [
        {
            "event_time": now,
            "item_type": row["item_type"],
            "item_name": row["item_name"],
            "relative_path": row["relative_path"],
            "action": "baseline",
            "summary": "initial paint status scan",
        }
        for row in status_rows
    ]


def project_number(item_name: str) -> str:
    match = re.match(r"(\d{2})", item_name)
    if match:
        return match.group(1)
    return "00"


def project_slug(item_name: str) -> str:
    return f"project-{project_number(item_name)}.html"


def meeting_slug(item_name: str) -> str:
    clean_name = item_name.removesuffix(".minutes.md")
    match = re.match(r"(\d{4}-\d{2}-\d{2})", clean_name)
    date_part = match.group(1) if match else "undated"
    digest = hashlib.sha1(item_name.encode("utf-8")).hexdigest()[:8]
    return f"meeting-{date_part}-{digest}.html"


def read_markdown_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) > 1 and all(re.fullmatch(r"[:\-\s]+", cell) for cell in rows[1]):
        rows.pop(1)
    if not rows:
        return ""

    head = "".join(f"<th>{inline_markdown(cell)}</th>" for cell in rows[0])
    body_rows = []
    for row in rows[1:]:
        body_rows.append("<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>")
    return (
        '<div class="table-wrap"><table>'
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )


def compact_list_continuations(markdown: str) -> str:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        stripped = raw_line.strip()
        if (
            raw_line[:1].isspace()
            and stripped
            and lines
            and re.match(r"^(\d+[.、]|[-*])\s+", lines[-1].strip())
        ):
            lines[-1] = lines[-1].rstrip() + " " + stripped
        else:
            lines.append(raw_line)

    compacted: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped and compacted and re.match(r"^(\d+[.、]|[-*])\s+", compacted[-1].strip()):
            next_line = next((candidate.strip() for candidate in lines[index + 1 :] if candidate.strip()), "")
            if re.match(r"^(\d+[.、]|[-*])\s+", next_line):
                continue
        compacted.append(line)
    return "\n".join(compacted)


def markdown_to_html(markdown: str) -> str:
    markdown = compact_list_continuations(markdown)
    output: list[str] = []
    paragraph: list[str] = []
    table_lines: list[str] = []
    list_type = ""

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            output.append(render_table(table_lines))
            table_lines = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = ""

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_table()
            close_list()
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            close_list()
            table_lines.append(stripped)
            continue

        flush_table()
        heading_match = re.match(r"^(#{3,4})\s+(.+)$", stripped)
        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered_match = re.match(r"^\d+[.、]\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            close_list()
            level = len(heading_match.group(1))
            output.append(f"<h{level}>{inline_markdown(heading_match.group(2))}</h{level}>")
        elif bullet_match:
            flush_paragraph()
            if list_type != "ul":
                close_list()
                output.append("<ul>")
                list_type = "ul"
            output.append(f"<li>{inline_markdown(bullet_match.group(1))}</li>")
        elif ordered_match:
            flush_paragraph()
            if list_type != "ol":
                close_list()
                output.append("<ol>")
                list_type = "ol"
            output.append(f"<li>{inline_markdown(ordered_match.group(1))}</li>")
        else:
            close_list()
            paragraph.append(stripped)

    flush_paragraph()
    flush_table()
    close_list()
    return "\n".join(output)


def read_project_meta() -> dict[str, dict[str, object]]:
    meta = dict(PROJECT_META)
    for row in read_csv(META_PATH):
        project_id = row.get("project_id", "").strip()
        if not project_id:
            continue
        meta[project_id] = {
            "tier": row.get("tier", "").strip(),
            "maturity": row.get("maturity", "").strip(),
            "domain": row.get("domain", "").strip(),
            "summary": row.get("summary", "").strip(),
            "key_numbers": [item.strip() for item in row.get("key_numbers", "").split("|") if item.strip()],
            "next_step": row.get("next_step", "").strip(),
            "risk": row.get("risk", "").strip(),
        }
    return meta


def build_projects(status_rows: list[dict[str, str]], project_meta: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    projects: list[dict[str, object]] = []
    for row in status_rows:
        if row["item_type"] != "project":
            continue
        project_dir = TEACHER_DIR / row["relative_path"]
        readme_path = project_dir / "README.md"
        text = read_text(readme_path) if readme_path.exists() else ""
        meta = project_meta.get(row["item_name"], {})
        projects.append(
            {
                "row": row,
                "meta": meta,
                "title": read_markdown_title(text, row["item_name"]),
                "sections": parse_sections(text),
                "slug": project_slug(row["item_name"]),
                "readme_href": repo_href(row["relative_path"] + "\\README.md"),
                "folder_href": repo_href(row["relative_path"]),
            }
        )
    return sorted(projects, key=lambda item: str(item["row"]["item_name"]))


def build_meetings(status_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    meetings: list[dict[str, object]] = []
    for row in status_rows:
        if row["item_type"] != "meeting_minutes":
            continue
        path = TEACHER_DIR / row["relative_path"]
        text = read_text(path) if path.exists() else ""
        sections = parse_sections(text)
        title = row["item_name"].removesuffix(".minutes.md")
        meetings.append(
            {
                "row": row,
                "title": title,
                "sections": sections,
                "href": meeting_slug(row["item_name"]),
                "source_href": repo_href(row["relative_path"]),
            }
        )
    return meetings


def event_anchor(event_id: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9_-]+", "-", event_id).strip("-")
    return f"event-{safe_id or 'item'}"


def event_type_label(event_type: str) -> str:
    return {
        "meeting": "会议",
        "milestone": "里程碑",
    }.get(event_type, event_type or "事件")


def event_status_label(status: str) -> str:
    return {
        "done": "已完成",
        "planned": "计划中",
    }.get(status, status or "未标记")


def event_status_sort_value(event: dict[str, object]) -> int:
    return {"done": 0, "planned": 1}.get(str(event.get("status", "")), 9)


def event_type_sort_value(event: dict[str, object]) -> int:
    return {"meeting": 0, "milestone": 1}.get(str(event.get("event_type", "")), 9)


def project_code(project_id: str) -> str:
    match = re.match(r"(\d{2})AI", project_id)
    if match:
        return f"P{match.group(1)}"
    return "项目"


def project_calendar_class(project_id: str) -> str:
    match = re.match(r"(\d{2})AI", project_id)
    if match:
        return f"project-p{match.group(1)}"
    return "project-other"


def event_sort_key(event: dict[str, object]) -> tuple[str, str]:
    date = str(event.get("date", ""))
    return (date or "9999-12-31", str(event.get("event_id", "")))


def event_date(event: dict[str, object]):
    try:
        return datetime.strptime(str(event.get("date", "")), "%Y-%m-%d").date()
    except ValueError:
        return None


def build_events(projects: list[dict[str, object]]) -> list[dict[str, object]]:
    project_by_id = {str(project["row"]["item_name"]): project for project in projects}
    events: list[dict[str, object]] = []
    for index, row in enumerate(read_csv(EVENTS_PATH), start=1):
        project_id = row.get("project_id", "").strip()
        project = project_by_id.get(project_id)
        if not project:
            continue
        raw_id = row.get("event_id", "").strip() or f"{project_id}-{index}"
        source_path = normalize_relative_path(row.get("source_path", "").strip())
        event = {
            "event_id": raw_id,
            "anchor": event_anchor(raw_id),
            "project_id": project_id,
            "project_title": str(project["title"]),
            "project_slug": str(project["slug"]),
            "date": row.get("date", "").strip(),
            "event_type": row.get("event_type", "").strip() or "milestone",
            "status": row.get("status", "").strip() or "planned",
            "title": row.get("title", "").strip() or "未命名事件",
            "summary": row.get("summary", "").strip(),
            "source_path": source_path,
            "source_href": repo_href(source_path) if source_path else "",
            "project_code": project_code(project_id),
            "project_class": project_calendar_class(project_id),
        }
        event["href"] = f'{event["project_slug"]}#{event["anchor"]}'
        events.append(event)
    return sorted(events, key=event_sort_key)


def project_events(events: list[dict[str, object]], project_name: str) -> list[dict[str, object]]:
    return [event for event in events if event.get("project_id") == project_name]


def attach_meeting_pages_to_events(events: list[dict[str, object]], meetings: list[dict[str, object]]) -> None:
    page_by_source = {
        normalize_relative_path(str(meeting["row"].get("relative_path", ""))): str(meeting.get("href", ""))
        for meeting in meetings
    }
    for event in events:
        if event.get("event_type") != "meeting":
            continue
        source_path = normalize_relative_path(str(event.get("source_path", "")))
        if source_path in page_by_source:
            event["meeting_href"] = page_by_source[source_path]


def meeting_date_from_title(title: str) -> str:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", title)
    return match.group(1) if match else ""


def meeting_event_for(meeting: dict[str, object], events: list[dict[str, object]]) -> dict[str, object] | None:
    meeting_path = normalize_relative_path(str(meeting["row"].get("relative_path", "")))  # type: ignore[index]
    for event in events:
        if event.get("event_type") != "meeting":
            continue
        if normalize_relative_path(str(event.get("source_path", ""))) == meeting_path:
            return event
    return None


def markdown_list_items(markdown: str, limit: int = 3) -> list[str]:
    items: list[str] = []
    for line in markdown.splitlines():
        text = line.strip()
        if not text:
            continue
        match = re.match(r"(?:[-*+]\s+(?:\[[ xX]\]\s*)?|\d+[.)]\s+)(.+)", text)
        if not match:
            continue
        item = re.sub(r"\*\*([^*]+)\*\*", r"\1", match.group(1)).strip()
        item = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item)
        if item:
            items.append(item)
        if len(items) >= limit:
            break
    if not items and markdown.strip():
        items.append(re.sub(r"\s+", " ", markdown.strip())[:180])
    return items


def render_mini_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f'<div class="empty">{html.escape(empty_text)}</div>'
    return '<ol class="meeting-mini-list">' + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ol>"


def nav_html(active: str) -> str:
    links = [
        ("index", "index.html", "总览"),
        ("projects", "projects.html", "项目进展"),
        ("meetings", "meetings.html", "会议记录"),
        ("updates", "updates.html", "更新时间"),
    ]
    nav = []
    for key, href, label in links:
        class_attr = ' class="active"' if key == active else ""
        nav.append(f'<a{class_attr} href="{href}">{label}</a>')
    return "\n".join(nav)


def page_shell(title: str, active: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">
        <strong>AI for Biology Progress</strong>
        <span>生物探索团队项目进展</span>
      </a>
      <nav class="nav" aria-label="主导航">
        {nav_html(active)}
      </nav>
    </div>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""


def status_badge(needs_update: str) -> str:
    if needs_update == "yes":
        return '<span class="badge red">待更新</span>'
    return '<span class="badge green">当前</span>'


def history_action_label(action: str) -> str:
    return {
        "baseline": "初始扫描",
        "updated": "已更新",
        "skipped": "已跳过",
        "created": "已创建",
    }.get(action, action)


def history_summary_label(summary: str) -> str:
    return {
        "initial paint status scan": "初始状态扫描",
    }.get(summary, summary)


def display_time(value: str) -> str:
    if not value:
        return "未记录"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M")


def compact_display_time(value: str) -> str:
    if not value:
        return "未记录"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%m-%d %H:%M")


def display_item_name(row: dict[str, str]) -> str:
    name = row.get("item_name", "")
    if row.get("item_type") == "meeting_minutes":
        name = name.removesuffix(".minutes.md")
    return name or row.get("relative_path", "未命名项目")


def item_type_label(item_type: str) -> str:
    return {
        "project": "项目",
        "meeting_minutes": "会议纪要",
    }.get(item_type, "记录")


def status_text(needs_update: str) -> str:
    return "需要同步" if needs_update == "yes" else "已同步"


def tier_badge(tier: str) -> str:
    if tier == "重点项目":
        return '<span class="badge teal">重点项目</span>'
    if tier == "数据资源能力":
        return '<span class="badge blue">数据资源</span>'
    if tier == "方法拓展":
        return '<span class="badge amber">方法拓展</span>'
    return '<span class="badge amber">待补齐</span>'


def project_card(project: dict[str, object], compact: bool = False) -> str:
    row = project["row"]
    meta = project["meta"]
    title = str(project["title"])
    slug = str(project["slug"])
    tier = str(meta.get("tier", "未分组"))
    maturity = str(meta.get("maturity", "待梳理"))
    summary = str(meta.get("summary", "该项目已形成研究问题、技术路线和当前进展说明。"))
    key_numbers = list(meta.get("key_numbers", []))
    stat_items = "".join(f"<li>{html.escape(str(item))}</li>" for item in key_numbers)
    if not stat_items:
        stat_items = "<li>等待关键数字提炼</li>"
    details = ""
    if not compact:
        details = f"""
        <div class="card-foot">
          <div><span>下一步</span> {html.escape(str(meta.get("next_step", "待从项目页收敛下一步行动。")))}</div>
          <div><span>边界</span> {html.escape(str(meta.get("risk", "暂无单独风险记录。")))}</div>
        </div>
        """
    return f"""
    <article class="project-card">
      <a class="project-card-link" href="{slug}" aria-label="打开{html.escape(title)}"></a>
      <div class="card-topline">
        {tier_badge(tier)}
        {status_badge(str(row["needs_update"]))}
      </div>
      <div>
        <h3>{html.escape(title)}</h3>
        <p>{html.escape(str(meta.get("domain", maturity)))}</p>
      </div>
      <p>{html.escape(summary)}</p>
      <ul class="stat-list">{stat_items}</ul>
      {details}
    </article>
    """


def render_calendar_event(event: dict[str, object]) -> str:
    type_label = event_type_label(str(event["event_type"]))
    status_label = event_status_label(str(event["status"]))
    project_title = str(event["project_title"])
    title = str(event["title"])
    access_label = f'{event.get("date", "")} {title}，{project_title}，{type_label}，{status_label}'
    class_tokens = " ".join(
        html.escape(str(token))
        for token in [
            "calendar-event",
            event.get("status", ""),
            event.get("event_type", ""),
            event.get("project_class", ""),
        ]
        if str(token)
    )
    return f"""
    <a class="{class_tokens}" href="{html.escape(str(event["href"]))}" title="{html.escape(access_label)}" aria-label="{html.escape(access_label)}">
      <span class="calendar-event-content">
        <span class="calendar-event-meta">
          <span class="project-pill">{html.escape(str(event.get("project_code", "项目")))}</span>
          <span>{html.escape(type_label)} · {html.escape(status_label)}</span>
        </span>
        <strong>{html.escape(title)}</strong>
        <span class="event-project-title">{html.escape(project_title)}</span>
      </span>
    </a>
    """


def render_calendar_month(
    year: int,
    month: int,
    events: list[dict[str, object]],
    max_visible_per_day: int | None = None,
) -> str:
    weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]
    today_key = datetime.now().astimezone().date().isoformat()
    events_by_date: dict[str, list[dict[str, object]]] = {}
    for event in events:
        events_by_date.setdefault(str(event.get("date", "")), []).append(event)

    first_weekday, days_in_month = calendar.monthrange(year, month)
    cells: list[str] = []
    for _ in range(first_weekday):
        cells.append('<div class="calendar-day empty" aria-hidden="true"></div>')

    for day in range(1, days_in_month + 1):
        date_key = f"{year:04d}-{month:02d}-{day:02d}"
        day_events = sorted(
            events_by_date.get(date_key, []),
            key=lambda item: (
                event_status_sort_value(item),
                event_type_sort_value(item),
                str(item.get("project_code", "")),
                str(item.get("event_id", "")),
            ),
        )
        visible_events = day_events
        overflow_events: list[dict[str, object]] = []
        if max_visible_per_day is not None and len(day_events) > max_visible_per_day:
            visible_events = day_events[:max_visible_per_day]
            overflow_events = day_events[max_visible_per_day:]
        event_html = "".join(render_calendar_event(event) for event in visible_events)
        if overflow_events:
            overflow_html = "".join(render_calendar_event(event) for event in overflow_events)
            event_html += f"""
              <details class="calendar-day-more">
                <summary>还有 {len(overflow_events)} 个节点</summary>
                <div class="calendar-overflow-events">
                  {overflow_html}
                </div>
              </details>
            """
        class_parts = ["calendar-day", "has-events" if day_events else "no-events"]
        if date_key == today_key:
            class_parts.append("today")
        count_label = f"<span>{len(day_events)} 个节点</span>" if day_events else "<span></span>"
        cells.append(
            f"""
            <div class="{' '.join(class_parts)}">
              <div class="calendar-date">{day}{count_label}</div>
              <div class="calendar-events">{event_html}</div>
            </div>
            """
        )

    while len(cells) % 7:
        cells.append('<div class="calendar-day empty" aria-hidden="true"></div>')

    weekdays = "".join(f'<div class="calendar-weekday">周{label}</div>' for label in weekday_labels)
    month_events = sum(1 for event in events if event_date(event) and event_date(event).year == year and event_date(event).month == month)
    return f"""
    <section class="calendar-month">
      <div class="calendar-month-title">
        <h3>{year}年{month}月</h3>
        <span>{month_events} 个节点</span>
      </div>
      <div class="calendar-grid">
        {weekdays}
        {''.join(cells)}
      </div>
    </section>
    """


def render_calendar_panel(
    events: list[dict[str, object]],
    panel_id: str,
    title: str,
    subtitle: str,
    empty_text: str,
    *,
    collapsible: bool = False,
    open_panel: bool = True,
    compact: bool = False,
    max_visible_per_day: int | None = None,
) -> str:
    valid_events = [event for event in events if event_date(event)]
    panel_classes = "calendar-panel"
    if compact:
        panel_classes += " compact-calendar"
    if not valid_events:
        return f"""
        <div class="{panel_classes}" id="{html.escape(panel_id)}">
          <div class="calendar-head">
            <h2>{html.escape(title)}</h2>
            <p>{html.escape(empty_text)}</p>
          </div>
        </div>
        """

    today = datetime.now().astimezone().date()
    done_count = sum(1 for event in valid_events if event.get("status") == "done")
    planned_count = sum(1 for event in valid_events if event.get("status") == "planned")
    project_count = len({event.get("project_id") for event in valid_events})
    upcoming = [
        event
        for event in valid_events
        if event.get("status") == "planned" and event_date(event) and event_date(event) >= today
    ]
    if upcoming:
        next_event = sorted(upcoming, key=event_sort_key)[0]
        next_label = f'{next_event["date"]} · {next_event["title"]}'
    else:
        next_label = "暂无后续计划节点"
    months = sorted({(event_date(event).year, event_date(event).month) for event in valid_events if event_date(event)})
    month_html = "".join(render_calendar_month(year, month, valid_events, max_visible_per_day) for year, month in months)
    summary_hint = f"{len(valid_events)} 个节点 · {planned_count} 个计划中 · {project_count} 个项目"
    calendar_inner = f"""
      <div class="calendar-summary">
        <div class="calendar-summary-item"><strong>{len(valid_events)}</strong><span>日程节点</span></div>
        <div class="calendar-summary-item"><strong>{done_count}</strong><span>已完成节点</span></div>
        <div class="calendar-summary-item"><strong>{planned_count}</strong><span>计划中节点</span></div>
        <div class="calendar-summary-item"><strong>{project_count}</strong><span>涉及项目；下一节点：{html.escape(str(next_label))}</span></div>
      </div>
      <div class="calendar-legend">
        <span class="legend-item"><span class="legend-dot meeting"></span>会议</span>
        <span class="legend-item"><span class="legend-dot done"></span>已完成节点</span>
        <span class="legend-item"><span class="legend-dot planned"></span>计划节点</span>
      </div>
      <div class="calendar-months">
        {month_html}
      </div>
    """
    body = f"""
      <div class="calendar-head">
        <h2>{html.escape(title)}</h2>
        <p>{html.escape(subtitle)}</p>
      </div>
      {calendar_inner}
    """
    if collapsible:
        open_attr = " open" if open_panel else ""
        return f"""
    <details class="{panel_classes} calendar-disclosure" id="{html.escape(panel_id)}"{open_attr}>
      <summary class="calendar-toggle">
        <span class="calendar-toggle-title">
          <strong>{html.escape(title)}</strong>
          <span>{html.escape(subtitle)}；{html.escape(summary_hint)}</span>
        </span>
        <span class="calendar-toggle-action">展开/收起</span>
      </summary>
      <div class="calendar-body">
        {calendar_inner}
      </div>
    </details>
    """
    return f"""
    <div class="{panel_classes}" id="{html.escape(panel_id)}">
      {body}
    </div>
    """


def render_home_calendar(events: list[dict[str, object]]) -> str:
    return render_calendar_panel(
        events,
        "project-calendar",
        "项目总日历",
        "会议和里程碑按日期归并，点击事件可跳转到对应项目区域",
        "暂无会议或里程碑记录",
        collapsible=True,
        open_panel=False,
        max_visible_per_day=2,
    )


def render_home(projects: list[dict[str, object]], meetings: list[dict[str, object]], status_rows: list[dict[str, str]], events: list[dict[str, object]], now: str) -> str:
    needs_update = sum(1 for row in status_rows if row["needs_update"] == "yes")
    featured = [p for p in projects if p["meta"].get("tier") == "重点项目"]
    evidence_ready = [
        p
        for p in projects
        if p["meta"].get("maturity") not in {"任务定义待补齐", "知识底座待定义"}
    ]
    stalled = [p for p in projects if p["meta"].get("tier") == "待启动/支撑方向"]

    featured_cards = "\n".join(project_card(project) for project in featured)
    meeting_cards = "\n".join(
        f"""
        <article class="insight-card">
          <h3>{html.escape(str(meeting["title"]))}</h3>
          {markdown_to_html(str(meeting["sections"].get("一句话概括", "暂无摘要。")))}
          <p><a class="text-link" href="meetings.html">查看会议记录</a></p>
        </article>
        """
        for meeting in meetings[:2]
    )

    body = f"""
    <section class="hero">
      <p class="eyebrow">生物探索团队 · 项目进展</p>
      <h1>AI 辅助生物探索项目进展总览</h1>
      <p class="lede">团队目前围绕生物机制理解、药物与递送、蛋白设计、疾病预测、反应设计和科学数据资源建设推进 10 个方向，已有多个项目形成可继续验证的阶段性结果。</p>
      <div class="meta-line">刷新时间：{html.escape(now)}</div>
      <div class="stat-strip">
        <div class="metric-card"><div class="metric-label">项目总数</div><div class="metric-value">{len(projects)}</div></div>
        <div class="metric-card"><div class="metric-label">重点项目</div><div class="metric-value">{len(featured)}</div></div>
        <div class="metric-card"><div class="metric-label">已有阶段成果</div><div class="metric-value">{len(evidence_ready)}</div></div>
        <div class="metric-card"><div class="metric-label">待更新项</div><div class="metric-value">{needs_update}</div></div>
      </div>
      {render_home_calendar(events)}
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>项目格局</h2>
          <p>当前项目分为生物主体方向、数据资源方向、方法拓展方向和待补齐支撑方向。</p>
        </div>
      </div>
      <div class="judgement-grid">
        <article class="insight-card">
          <h3>生物主体方向</h3>
          <p>AI-BAT、老药新用、抗冻肽、IDP ensemble、胃癌预测构成当前生物问题主线。</p>
        </article>
        <article class="insight-card">
          <h3>数据资源方向</h3>
          <p>级联催化和 OPV 已形成文献知识结构化、质量分层和 benchmark 准备基础。</p>
        </article>
        <article class="insight-card">
          <h3>方法扩展</h3>
          <p>吸附质放置用于说明 flow matching 和科学计算方法可迁移方向。</p>
        </article>
        <article class="insight-card">
          <h3>待补齐方向</h3>
          <p>LNP 和生物化学需要先收敛应用场景、变量体系和任务边界。</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>重点项目</h2>
          <p>这些方向已经形成较清晰的问题定义、计算路线或阶段性结果。</p>
        </div>
        <a class="text-link" href="projects.html">全部项目</a>
      </div>
      <div class="project-grid">
        {featured_cards}
      </div>
    </section>

    <section class="section two-col">
      <div class="panel">
        <h2>下一阶段推进</h2>
        <ol class="action-list">
          <li>为 5 个重点项目沉淀清晰的问题、证据、结果和下一步验证任务。</li>
          <li>为老药新用、抗冻肽、ThermoProt 补齐结果图表、候选表或 benchmark 对照。</li>
          <li>让级联催化从数据集介绍转入“路线级联可行性评估器”小验证。</li>
          <li>将 LNP 和生物化学明确为待启动方向或支撑模块，并补齐可执行任务。</li>
          <li>把会议行动项映射回具体项目，而不是停留在会议纪要列表。</li>
        </ol>
      </div>
      <div class="panel">
        <h2>需要补齐</h2>
        <ul class="plain-list">
          <li>待启动/支撑方向：{len(stalled)} 个。</li>
          <li>项目负责人字段仍多为待填写。</li>
          <li>部分项目需要从材料整理转成结果图表。</li>
          <li>对 claim boundary 的表述需要继续统一。</li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>近期讨论</h2>
          <p>近期讨论沉淀出分子生成机制理解和级联反应路径规划两条后续任务。</p>
        </div>
        <a class="text-link" href="meetings.html">会议记录</a>
      </div>
      <div class="judgement-grid">
        {meeting_cards or '<div class="empty">暂无会议纪要。</div>'}
      </div>
    </section>
    """
    return page_shell("AI-for-biology-progress 项目进展", "index", body)


def render_projects_page(projects: list[dict[str, object]], now: str) -> str:
    groups = [
        ("重点项目", "生物主体项目，已形成较清晰的问题定义、阶段结果或验证路线。"),
        ("数据资源能力", "复杂科学文献已经转成可审计、可筛选、可建模的数据资产。"),
        ("方法拓展", "用于说明方法储备和潜在迁移方向。"),
        ("待启动/支撑方向", "需要先补齐任务定义或作为支撑模块处理。"),
    ]
    sections = []
    for tier, description in groups:
        grouped = [project for project in projects if project["meta"].get("tier") == tier]
        if not grouped:
            continue
        cards = "\n".join(project_card(project) for project in grouped)
        sections.append(
            f"""
            <section class="section">
              <div class="section-head">
                <div>
                  <h2>{html.escape(tier)}</h2>
                  <p>{html.escape(description)}</p>
                </div>
              </div>
              <div class="project-grid">{cards}</div>
            </section>
            """
        )

    rows = []
    for project in projects:
        row = project["row"]
        meta = project["meta"]
        rows.append(
            "<tr>"
            f'<td><a href="{project["slug"]}">{html.escape(str(project["title"]))}</a></td>'
            f"<td>{html.escape(str(meta.get('tier', '未分组')))}</td>"
            f"<td>{html.escape(str(meta.get('maturity', '待梳理')))}</td>"
            f"<td>{html.escape(str(meta.get('next_step', '待收敛')))}</td>"
            f"<td>{status_badge(str(row['needs_update']))}</td>"
            "</tr>"
        )

    body = f"""
    <section class="hero">
      <p class="eyebrow">项目进展</p>
      <h1>10 个 AI 辅助科学探索方向</h1>
      <p class="lede">项目按研究成熟度和任务类型组织，覆盖生物机制、药物筛选、功能肽发现、蛋白构象生成、疾病预测、反应设计和材料数据资源。</p>
      <div class="meta-line">刷新时间：{html.escape(now)}</div>
    </section>

    {''.join(sections)}

    <section class="section">
      <div class="section-head">
        <div>
          <h2>项目总表</h2>
          <p>用于快速比较成熟度、下一步和更新状态。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>项目</th><th>项目类别</th><th>成熟度</th><th>下一步</th><th>状态</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </section>
    """
    return page_shell("项目进展", "projects", body)


def render_event_card(event: dict[str, object]) -> str:
    source_link = ""
    if event.get("meeting_href"):
        source_link = f'<a href="{html.escape(str(event["meeting_href"]))}">会议页</a>'
    elif event.get("event_type") != "meeting" and event.get("source_href"):
        source_link = f'<a href="{html.escape(str(event["source_href"]))}">来源记录</a>'
    return f"""
    <article class="event-card {html.escape(str(event["status"]))} {html.escape(str(event["event_type"]))}" id="{html.escape(str(event["anchor"]))}">
      <div class="event-meta">
        <span>{html.escape(str(event["date"]))}</span>
        <span>{html.escape(event_type_label(str(event["event_type"])))}</span>
        <span>{html.escape(event_status_label(str(event["status"])))}</span>
      </div>
      <h4>{html.escape(str(event["title"]))}</h4>
      <p>{html.escape(str(event["summary"]))}</p>
      <div class="event-links">
        <a href="index.html#project-calendar">首页项目日历</a>
        <a href="#project-local-calendar">本项目日历</a>
        {source_link}
      </div>
    </article>
    """


def render_project_events(project: dict[str, object], events: list[dict[str, object]]) -> str:
    related = project_events(events, str(project["row"]["item_name"]))
    meetings = [event for event in related if event.get("event_type") == "meeting"]
    milestones = [event for event in related if event.get("event_type") != "meeting"]
    title = str(project["title"])
    project_calendar_html = render_calendar_panel(
        related,
        "project-local-calendar",
        "本项目日历",
        "当前项目的会议、里程碑和计划节点",
        "暂无本项目日程节点。",
        compact=True,
    )

    def group(events_for_group: list[dict[str, object]], empty_text: str) -> str:
        if not events_for_group:
            return f'<div class="empty">{html.escape(empty_text)}</div>'
        return "\n".join(render_event_card(event) for event in events_for_group)

    return f"""
    <section class="section project-events" id="project-events">
      <div class="section-head">
        <div>
          <h2>项目日程</h2>
          <p>仅显示 {html.escape(title)} 的会议和里程碑；这些节点来自首页项目总日历的同一组记录。</p>
        </div>
        <a class="text-link" href="index.html#project-calendar">返回总日历</a>
      </div>
      {project_calendar_html}
      <div class="event-sections">
        <section class="event-group" id="meeting-nodes">
          <h3>会议节点</h3>
          {group(meetings, "暂无会议节点。")}
        </section>
        <section class="event-group" id="milestone-nodes">
          <h3>里程碑区域</h3>
          {group(milestones, "暂无里程碑节点。")}
        </section>
      </div>
    </section>
    """


def render_project_page(project: dict[str, object], now: str, events: list[dict[str, object]]) -> str:
    row = project["row"]
    meta = project["meta"]
    title = str(project["title"])
    sections: dict[str, str] = project["sections"]  # type: ignore[assignment]
    section_order = ["基本信息", "研究问题", "研究意义", "项目目标", "技术路线", "当前进展"]
    content_sections = []
    for section_name in section_order:
        markdown = sections.get(section_name, "")
        if not markdown:
            continue
        content_sections.append(
            f"""
            <section class="md-section">
              <h2>{html.escape(section_name)}</h2>
              {markdown_to_html(markdown)}
            </section>
            """
        )

    facts = [
        ("项目类别", str(meta.get("tier", "未分组"))),
        ("成熟度", str(meta.get("maturity", "待梳理"))),
        ("研究方向", str(meta.get("domain", "见项目正文"))),
        ("材料最后修改", str(row.get("latest_source_mtime", "") or "无材料文件")),
        ("内容最后更新", str(row.get("last_content_update", ""))),
        ("刷新状态", "待更新" if row.get("needs_update") == "yes" else "当前"),
    ]
    fact_rows = "\n".join(
        f'<div class="fact-row"><div class="fact-label">{html.escape(label)}</div><div class="fact-value">{html.escape(value)}</div></div>'
        for label, value in facts
    )
    key_numbers = "".join(f"<li>{html.escape(str(item))}</li>" for item in meta.get("key_numbers", []))
    body = f"""
    <section class="hero">
      <p class="eyebrow">项目详情</p>
      <h1>{html.escape(title)}</h1>
      <p class="lede">{html.escape(str(meta.get("summary", "项目已形成研究问题、技术路线和当前进展说明。")))}</p>
      <div class="meta-line">刷新时间：{html.escape(now)}</div>
    </section>

    <section class="section project-detail">
      <div class="content-stack">
        {''.join(content_sections) or '<div class="empty">README 尚未形成标准项目正文。</div>'}
      </div>
      <aside class="side-panel">
        <div class="panel">
          <h2>项目定位</h2>
          {fact_rows}
        </div>
        <div class="panel">
          <h2>关键数字</h2>
          <ul class="plain-list">{key_numbers or '<li>待从项目材料中提炼。</li>'}</ul>
        </div>
        <div class="panel">
          <h2>下一步与边界</h2>
          <p><strong>下一步：</strong>{html.escape(str(meta.get("next_step", "待收敛下一步行动。")))}</p>
          <p><strong>边界：</strong>{html.escape(str(meta.get("risk", "暂无单独风险记录。")))}</p>
          <p><a class="text-link" href="{project["readme_href"]}">项目源文档</a></p>
        </div>
      </aside>
    </section>
    {render_project_events(project, events)}
    """
    return page_shell(title, "projects", body)


def render_meeting_node_card(event: dict[str, object]) -> str:
    source_link = ""
    if event.get("meeting_href"):
        source_link = f'<a href="{html.escape(str(event["meeting_href"]))}">会议页</a>'
    return f"""
    <article class="meeting-brief-card meeting-node-card {html.escape(str(event.get("status", "")))}">
      <div class="meeting-tagline">
        <span>{html.escape(str(event.get("date", "")))}</span>
        <span>{html.escape(event_status_label(str(event.get("status", ""))))}</span>
        <span>{html.escape(str(event.get("project_code", "项目")))}</span>
      </div>
      <h3>{html.escape(str(event.get("title", "未命名会议")))}</h3>
      <p>{html.escape(str(event.get("summary", "")) or str(event.get("project_title", "")))}</p>
      <div class="meeting-link-row">
        <a href="{html.escape(str(event.get("href", "#")))}">项目节点</a>
        {source_link}
      </div>
    </article>
    """


def render_meetings_page(meetings: list[dict[str, object]], events: list[dict[str, object]], now: str) -> str:
    meeting_events = [event for event in events if event.get("event_type") == "meeting"]
    meeting_events = sorted(meeting_events, key=event_sort_key)
    planned_meetings = [event for event in meeting_events if event.get("status") == "planned"]
    related_project_count = len({event.get("project_id") for event in meeting_events})
    source_count = sum(1 for meeting in meetings if str(meeting["row"].get("relative_path", "")))  # type: ignore[index]

    node_cards = "".join(render_meeting_node_card(event) for event in meeting_events)
    brief_cards = []
    detail_cards = []
    action_cards = []

    sorted_meetings = sorted(meetings, key=lambda item: meeting_date_from_title(str(item["title"])), reverse=True)
    for meeting in sorted_meetings:
        sections: dict[str, str] = meeting["sections"]  # type: ignore[assignment]
        linked_event = meeting_event_for(meeting, events)
        meeting_date = str(linked_event.get("date", "")) if linked_event else meeting_date_from_title(str(meeting["title"]))
        project_title = str(linked_event.get("project_title", "未绑定项目节点")) if linked_event else "未绑定项目节点"
        project_link = str(linked_event.get("href", "")) if linked_event else ""
        core_items = markdown_list_items(sections.get("核心结论", ""), 2)
        direction_items = markdown_list_items(sections.get("可行方向", ""), 2)
        action_items = markdown_list_items(sections.get("下一步行动", ""), 5)
        first_line = core_items[0] if core_items else "暂无核心结论。"
        project_node_link = f'<a href="{html.escape(project_link)}">项目节点</a>' if project_link else ""
        brief_cards.append(
            f"""
            <article class="meeting-brief-card">
              <div class="meeting-card-meta">
                <span>{html.escape(meeting_date or "日期待补")}</span>
                <span>{html.escape(project_title)}</span>
              </div>
              <h3>{html.escape(str(meeting["title"]))}</h3>
              <p>{html.escape(first_line)}</p>
              <div class="meeting-link-row">
                {project_node_link}
                <a href="{html.escape(str(meeting["href"]))}">会议页</a>
              </div>
            </article>
            """
        )
        action_cards.append(
            f"""
            <article class="action-card">
              <h3>{html.escape(str(meeting["title"]))}</h3>
              {render_mini_list(action_items, "暂无行动项。")}
            </article>
            """
        )
        detail_cards.append(
            f"""
            <details class="meeting-card meeting-detail">
              <summary>
                <div>
                  <h2>{html.escape(str(meeting["title"]))}</h2>
                  <span class="meeting-card-meta">
                    <span>{html.escape(meeting_date or "日期待补")}</span>
                    <span>{html.escape(project_title)}</span>
                  </span>
                </div>
              </summary>
              <div class="meeting-detail-body">
                <p class="meta-line"><a href="{html.escape(str(meeting["href"]))}">独立会议页</a></p>
                <div class="meeting-columns">
                  <section>
                    <h3>核心结论</h3>
                    {render_mini_list(core_items, "暂无核心结论。")}
                  </section>
                  <section>
                    <h3>可行方向</h3>
                    {render_mini_list(direction_items, "暂无可行方向。")}
                  </section>
                </div>
                <section>
                  <h3>下一步行动</h3>
                  {render_mini_list(action_items, "暂无下一步行动。")}
                </section>
                <section>
                  <h3>完整记录</h3>
                  <div class="meeting-columns">
                    <section>
                      <h3>核心结论</h3>
                      {markdown_to_html(sections.get("核心结论", "暂无核心结论。"))}
                    </section>
                    <section>
                      <h3>可行方向</h3>
                      {markdown_to_html(sections.get("可行方向", "暂无可行方向。"))}
                    </section>
                  </div>
                  <h3>下一步行动</h3>
                  {markdown_to_html(sections.get("下一步行动", "暂无下一步行动。"))}
                </section>
              </div>
            </details>
            """
        )

    action_total = sum(
        len(markdown_list_items(str(meeting["sections"].get("下一步行动", "")), 100))  # type: ignore[index]
        for meeting in meetings
    )
    next_meeting_label = "暂无计划中会议"
    if planned_meetings:
        next_meeting = sorted(planned_meetings, key=event_sort_key)[0]
        next_meeting_label = f'{next_meeting["date"]} · {next_meeting["title"]}'

    body = f"""
    <section class="hero">
      <p class="eyebrow">会议记录</p>
      <h1>会议节点与行动项</h1>
      <p class="lede">会议页按日期、项目和行动项组织；已完成会议保留纪要摘要，计划会议进入同一会议日历。</p>
      <div class="meta-line">刷新时间：{html.escape(now)}</div>
      <div class="meeting-dashboard">
        <div class="metric-card"><div class="metric-label">会议节点</div><div class="metric-value">{len(meeting_events)}</div></div>
        <div class="metric-card"><div class="metric-label">已归档纪要</div><div class="metric-value">{source_count}</div></div>
        <div class="metric-card"><div class="metric-label">涉及项目</div><div class="metric-value">{related_project_count}</div></div>
        <div class="metric-card"><div class="metric-label">行动项</div><div class="metric-value">{action_total}</div></div>
      </div>
    </section>

    {render_calendar_panel(
        meeting_events,
        "meeting-calendar",
        "会议日历",
        f"已完成会议和计划会议按日期组织；下一场：{next_meeting_label}",
        "暂无会议节点。",
        collapsible=True,
        open_panel=False,
        compact=True,
        max_visible_per_day=2,
    )}

    <section class="section">
      <div class="section-head">
        <div>
          <h2>会议节点</h2>
          <p>所有会议节点都可跳转到对应项目区域；计划会议没有纪要时只保留项目节点。</p>
        </div>
      </div>
      <div class="meeting-brief-grid">
        {node_cards or '<div class="empty">暂无会议节点。</div>'}
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>纪要摘要</h2>
          <p>每条纪要提取核心判断和对应项目，完整内容在下方可展开。</p>
        </div>
      </div>
      <div class="meeting-brief-grid">
        {''.join(brief_cards) or '<div class="empty">暂无会议纪要。</div>'}
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>行动项</h2>
          <p>行动项按会议归并，便于直接对应后续推进。</p>
        </div>
      </div>
      <div class="action-board">
        {''.join(action_cards) or '<div class="empty">暂无行动项。</div>'}
      </div>
    </section>

    <section class="section meeting-grid">
      <div class="section-head">
        <div>
          <h2>完整纪要</h2>
          <p>展开后查看完整核心结论、可行方向和下一步行动。</p>
        </div>
      </div>
      {''.join(detail_cards) or '<div class="empty">暂无会议纪要。</div>'}
    </section>
    """
    return page_shell("会议记录", "meetings", body)


def render_meeting_page(meeting: dict[str, object], events: list[dict[str, object]], now: str) -> str:
    sections: dict[str, str] = meeting["sections"]  # type: ignore[assignment]
    linked_event = meeting_event_for(meeting, events)
    meeting_date = str(linked_event.get("date", "")) if linked_event else meeting_date_from_title(str(meeting["title"]))
    project_title = str(linked_event.get("project_title", "未绑定项目节点")) if linked_event else "未绑定项目节点"
    project_link = str(linked_event.get("href", "")) if linked_event else ""
    status_label = event_status_label(str(linked_event.get("status", ""))) if linked_event else "已归档"
    core_items = markdown_list_items(sections.get("核心结论", ""), 2)
    action_count = len(markdown_list_items(sections.get("下一步行动", ""), 100))
    lede = core_items[0] if core_items else "会议纪要已整理为核心结论、可行方向和下一步行动。"
    project_link_html = f'<a class="text-link" href="{html.escape(project_link)}">对应项目节点</a>' if project_link else ""

    body = f"""
    <section class="hero">
      <p class="eyebrow">会议纪要</p>
      <h1>{html.escape(str(meeting["title"]))}</h1>
      <p class="lede">{html.escape(lede)}</p>
      <div class="meta-line">刷新时间：{html.escape(now)}</div>
      <div class="meeting-dashboard">
        <div class="metric-card"><div class="metric-label">会议日期</div><div class="metric-value">{html.escape(meeting_date[-2:] if meeting_date else "--")}</div></div>
        <div class="metric-card"><div class="metric-label">状态</div><div class="metric-value">{html.escape(status_label)}</div></div>
        <div class="metric-card"><div class="metric-label">关联项目</div><div class="metric-value">{html.escape(str(linked_event.get("project_code", "项目") if linked_event else "--"))}</div></div>
        <div class="metric-card"><div class="metric-label">行动项</div><div class="metric-value">{action_count}</div></div>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>会议定位</h2>
          <p>{html.escape(project_title)} · {html.escape(meeting_date or "日期待补")}</p>
        </div>
        <div class="meeting-link-row">
          <a class="text-link" href="meetings.html">返回会议记录</a>
          {project_link_html}
        </div>
      </div>
    </section>

    <section class="section meeting-columns">
      <article class="action-card">
        <h3>核心结论</h3>
        {markdown_to_html(sections.get("核心结论", "暂无核心结论。"))}
      </article>
      <article class="action-card">
        <h3>可行方向</h3>
        {markdown_to_html(sections.get("可行方向", "暂无可行方向。"))}
      </article>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>下一步行动</h2>
          <p>从会议纪要中整理出的后续推进事项。</p>
        </div>
      </div>
      <div class="action-card">
        {markdown_to_html(sections.get("下一步行动", "暂无下一步行动。"))}
      </div>
    </section>
    """
    return page_shell(str(meeting["title"]), "meetings", body)


def render_updates_page(status_rows: list[dict[str, str]], history_rows: list[dict[str, str]], now: str) -> str:
    projects = [row for row in status_rows if row["item_type"] == "project"]
    meetings = [row for row in status_rows if row["item_type"] == "meeting_minutes"]

    def item_link(row: dict[str, str]) -> str:
        if row.get("item_type") == "project":
            return project_slug(row.get("item_name", ""))
        return meeting_slug(row.get("item_name", ""))

    def link_text(row: dict[str, str]) -> str:
        return "打开项目" if row.get("item_type") == "project" else "打开纪要"

    def source_time_label(row: dict[str, str]) -> str:
        return "材料修改" if row.get("item_type") == "project" else "纪要修改"

    def source_time_value(row: dict[str, str]) -> str:
        if row.get("latest_source_mtime"):
            return display_time(row.get("latest_source_mtime", ""))
        if row.get("item_type") == "project":
            return "无额外材料"
        return "未记录"

    def sync_card(row: dict[str, str]) -> str:
        title = display_item_name(row)
        return f"""
        <article class="sync-card">
          <div class="sync-card-head">
            <div>
              <span class="sync-type">{html.escape(item_type_label(row.get("item_type", "")))}</span>
              <h3>{html.escape(title)}</h3>
            </div>
            {status_badge(row.get("needs_update", ""))}
          </div>
          <div class="time-pair">
            <div class="time-item">
              <span>{html.escape(source_time_label(row))}</span>
              <strong>{html.escape(source_time_value(row))}</strong>
            </div>
            <div class="time-item">
              <span>内容同步</span>
              <strong>{html.escape(display_time(row.get("last_content_update", "")))}</strong>
            </div>
          </div>
          <p class="sync-note">最近扫描：{html.escape(display_time(row.get("last_scanned_at", "")))} · {html.escape(status_text(row.get("needs_update", "")))}</p>
          <div class="meeting-link-row">
            <a href="{html.escape(item_link(row))}">{html.escape(link_text(row))}</a>
          </div>
        </article>
        """

    def history_item(row: dict[str, str]) -> str:
        title = display_item_name(row)
        href = item_link(row)
        detail = f'{item_type_label(row.get("item_type", ""))} · {history_action_label(row.get("action", ""))} · {history_summary_label(row.get("summary", ""))}'
        return f"""
        <li class="activity-item">
          <span class="activity-time">{html.escape(compact_display_time(row.get("event_time", "")))}</span>
          <span class="activity-title">
            <strong>{html.escape(title)}</strong>
            <span>{html.escape(detail)}</span>
          </span>
          <a class="text-link" href="{html.escape(href)}">查看</a>
        </li>
        """

    project_cards = "".join(sync_card(row) for row in projects)
    meeting_cards = "".join(sync_card(row) for row in meetings)
    recent_history = list(reversed(history_rows[-20:]))
    history_items = "".join(history_item(row) for row in recent_history)
    needs_update = sum(1 for row in status_rows if row.get("needs_update") == "yes")
    current_items = len(status_rows) - needs_update
    source_records = sum(1 for row in status_rows if row.get("latest_source_mtime"))
    latest_scan = max((row.get("last_scanned_at", "") for row in status_rows), default=now)

    body = f"""
    <section class="hero">
      <p class="eyebrow">更新时间</p>
      <h1>内容同步状态</h1>
      <p class="lede">这里展示项目页面、项目材料和会议纪要之间的同步状态；路径和原始扫描字段收进链接与更新流水中。</p>
      <div class="meta-line">最近扫描：{html.escape(display_time(latest_scan))}</div>
      <div class="update-dashboard">
        <div class="metric-card"><div class="metric-label">同步记录</div><div class="metric-value">{len(status_rows)}</div></div>
        <div class="metric-card"><div class="metric-label">已同步</div><div class="metric-value">{current_items}</div></div>
        <div class="metric-card"><div class="metric-label">需要同步</div><div class="metric-value">{needs_update}</div></div>
        <div class="metric-card"><div class="metric-label">有材料来源</div><div class="metric-value">{source_records}</div></div>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>项目同步</h2>
          <p>每张卡片比较项目材料最后修改时间和页面内容同步时间。</p>
        </div>
      </div>
      <div class="sync-grid">
        {project_cards or '<div class="empty">暂无项目同步记录。</div>'}
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>会议纪要同步</h2>
          <p>只展示已归档的 .minutes.md 纪要，原始转写不进入这个视图。</p>
        </div>
      </div>
      <div class="sync-grid meeting-sync-grid">
        {meeting_cards or '<div class="empty">暂无会议纪要同步记录。</div>'}
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>最近同步活动</h2>
          <p>保留最近 20 条扫描或更新记录，用于追踪页面内容何时被刷新。</p>
        </div>
      </div>
      <ul class="activity-feed">
        {history_items or '<li class="empty">暂无同步活动。</li>'}
      </ul>
    </section>
    """
    return page_shell("更新时间", "updates", body)


def main() -> None:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    existing_rows = read_csv(STATUS_PATH)
    existing_by_path = {
        normalize_relative_path(row.get("relative_path", "")): row
        for row in existing_rows
    }

    status_rows = project_rows(existing_by_path, now) + meeting_rows(existing_by_path, now)
    history_rows = [
        row for row in read_csv(HISTORY_PATH) if row.get("item_type") != "meeting_transcript"
    ]
    for row in history_rows:
        row["relative_path"] = normalize_relative_path(row.get("relative_path", ""))
    history_rows = ensure_history(history_rows, status_rows, now)

    write_csv(STATUS_PATH, status_rows, STATUS_FIELDS)
    write_csv(HISTORY_PATH, history_rows, HISTORY_FIELDS)

    projects = build_projects(status_rows, read_project_meta())
    meetings = build_meetings(status_rows)
    events = build_events(projects)
    attach_meeting_pages_to_events(events, meetings)

    write_generated(CSS_PATH, STYLE_CSS)
    write_generated(HTML_PATH, render_home(projects, meetings, status_rows, events, now))
    write_generated(PAINT_DIR / "projects.html", render_projects_page(projects, now))
    write_generated(PAINT_DIR / "meetings.html", render_meetings_page(meetings, events, now))
    write_generated(PAINT_DIR / "updates.html", render_updates_page(status_rows, history_rows, now))
    for project in projects:
        write_generated(PAINT_DIR / str(project["slug"]), render_project_page(project, now, events))
    for meeting in meetings:
        write_generated(PAINT_DIR / str(meeting["href"]), render_meeting_page(meeting, events, now))

    generated = [
        STATUS_PATH,
        HTML_PATH,
        PAINT_DIR / "projects.html",
        PAINT_DIR / "meetings.html",
        PAINT_DIR / "updates.html",
        CSS_PATH,
    ] + [PAINT_DIR / str(project["slug"]) for project in projects] + [PAINT_DIR / str(meeting["href"]) for meeting in meetings]
    for path in generated:
        print(str(path.relative_to(TEACHER_DIR.parent)).replace("/", "\\"))


if __name__ == "__main__":
    main()
