import csv
import html
from datetime import datetime
from pathlib import Path


PAINT_DIR = Path(__file__).resolve().parent
TEACHER_DIR = PAINT_DIR.parent
STATUS_PATH = PAINT_DIR / "update_status.csv"
HISTORY_PATH = PAINT_DIR / "update_history.csv"
HTML_PATH = PAINT_DIR / "index.html"

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


def rel(path: Path) -> str:
    return str(path.relative_to(TEACHER_DIR)).replace("/", "\\")


def iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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
        latest_source = latest_project_source_mtime(project_dir)
        last_content_update = old.get("last_content_update") or iso_from_timestamp(
            (project_dir / "README.md").stat().st_mtime
        )
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


def status_badge(needs_update: str) -> str:
    if needs_update == "yes":
        return '<span class="badge hot">needs update</span>'
    return '<span class="badge ok">current</span>'


def render_html(status_rows: list[dict[str, str]], history_rows: list[dict[str, str]], now: str) -> str:
    projects = [row for row in status_rows if row["item_type"] == "project"]
    meetings = [row for row in status_rows if row["item_type"] == "meeting_minutes"]
    needs_update = sum(1 for row in status_rows if row["needs_update"] == "yes")

    def table(rows: list[dict[str, str]], source_label: str) -> str:
        body = []
        for row in rows:
            body.append(
                "<tr>"
                f"<td>{html.escape(row['item_name'])}</td>"
                f"<td>{html.escape(row[source_label])}</td>"
                f"<td>{html.escape(row['last_content_update'])}</td>"
                f"<td>{status_badge(row['needs_update'])}</td>"
                "</tr>"
            )
        return "\n".join(body)

    history_items = "\n".join(
        "<li>"
        f"<strong>{html.escape(row['event_time'])}</strong> "
        f"{html.escape(row['action'])} "
        f"<code>{html.escape(row['relative_path'])}</code> "
        f"{html.escape(row['summary'])}"
        "</li>"
        for row in history_rows[-30:]
    )

    def meeting_table(rows: list[dict[str, str]]) -> str:
        body = []
        for row in rows:
            body.append(
                "<tr>"
                f"<td>{html.escape(row['item_name'])}</td>"
                f"<td><code>{html.escape(row['relative_path'])}</code></td>"
                f"<td>{html.escape(row['latest_source_mtime'])}</td>"
                f"<td>{html.escape(row['last_content_update'])}</td>"
                f"<td>{status_badge(row['needs_update'])}</td>"
                "</tr>"
            )
        return "\n".join(body)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI-for-biology-progress 更新记录</title>
  <style>
    body {{ font-family: Arial, "Microsoft YaHei", sans-serif; margin: 0; color: #17212b; background: #f6f7f9; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 44px; }}
    h1 {{ margin: 0; font-size: 24px; }}
    h2 {{ margin: 28px 0 10px; font-size: 17px; }}
    .meta {{ color: #64707d; margin: 8px 0 18px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 18px; }}
    .card {{ background: #fff; border: 1px solid #d9dee7; border-radius: 6px; padding: 12px; }}
    .label {{ color: #64707d; font-size: 13px; }}
    .num {{ font-size: 26px; font-weight: 700; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d9dee7; }}
    th, td {{ border-bottom: 1px solid #e7eaf0; padding: 9px 10px; vertical-align: top; text-align: left; font-size: 13px; }}
    th {{ background: #f0f2f5; color: #4b5563; font-weight: 600; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{ font-family: Consolas, monospace; font-size: 13px; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 3px 8px; font-size: 12px; }}
    .ok {{ background: #dff3e4; color: #1f6b3a; }}
    .hot {{ background: #ffe2df; color: #9b2c1f; }}
    ol {{ background: #fff; border: 1px solid #d9dee7; margin: 0; padding: 12px 18px 12px 34px; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <main>
  <h1>AI-for-biology-progress 更新记录</h1>
  <div class="meta">刷新时间：{html.escape(now)}</div>

  <div class="cards">
    <div class="card"><div class="label">项目文件夹</div><div class="num">{len(projects)}</div></div>
    <div class="card"><div class="label">会议总结</div><div class="num">{len(meetings)}</div></div>
    <div class="card"><div class="label">待更新项</div><div class="num">{needs_update}</div></div>
  </div>

  <h2>项目状态</h2>
  <table>
    <thead><tr><th>项目</th><th>材料最后修改</th><th>内容最后更新</th><th>状态</th></tr></thead>
    <tbody>{table(projects, "latest_source_mtime")}</tbody>
  </table>

  <h2>会议总结</h2>
  <table>
    <thead><tr><th>名称</th><th>路径</th><th>文件最后修改</th><th>内容最后更新</th><th>状态</th></tr></thead>
    <tbody>{meeting_table(meetings)}</tbody>
  </table>

  <h2>最近记录</h2>
  <ol>{history_items}</ol>
  </main>
</body>
</html>
"""


def main() -> None:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    existing_rows = read_csv(STATUS_PATH)
    existing_by_path = {row["relative_path"]: row for row in existing_rows}

    status_rows = project_rows(existing_by_path, now) + meeting_rows(existing_by_path, now)
    history_rows = [
        row for row in read_csv(HISTORY_PATH) if row.get("item_type") != "meeting_transcript"
    ]
    for row in history_rows:
        row["relative_path"] = normalize_relative_path(row.get("relative_path", ""))
    history_rows = ensure_history(history_rows, status_rows, now)

    write_csv(STATUS_PATH, status_rows, STATUS_FIELDS)
    write_csv(HISTORY_PATH, history_rows, HISTORY_FIELDS)
    HTML_PATH.write_text(render_html(status_rows, history_rows, now), encoding="utf-8")

    print(str(STATUS_PATH.relative_to(TEACHER_DIR.parent)).replace("/", "\\"))
    print(str(HTML_PATH.relative_to(TEACHER_DIR.parent)).replace("/", "\\"))


if __name__ == "__main__":
    main()
