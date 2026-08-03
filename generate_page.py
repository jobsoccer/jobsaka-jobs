"""jleague_jobs.md を読み込み、「今週のJリーグ求人」ページ（docs/index.html）を生成する。"""
import html
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE = Path("jleague_jobs.md")
OUTPUT = Path("docs/index.html")
MAX_ENTRIES = 20
JST = timezone(timedelta(hours=9))


def parse_entries(text: str) -> list[dict]:
    blocks = re.split(r"\n-{3,}\n", text)
    entries = []
    for block in blocks:
        block = block.strip()
        block = re.sub(r"^-{3,}\s*\n", "", block).strip()
        if not block.startswith("##"):
            continue

        title_match = re.search(r"^##\s*(.+?)\s*[|｜]\s*(.+)$", block, re.MULTILINE)
        if not title_match:
            continue

        date_match = re.search(r"📅\s*取得日時[：:]\s*(.+)", block)
        company_match = re.search(r"🏢\s*掲載企業[：:]\s*(.+)", block)
        employment_match = re.search(r"💼\s*雇用形態[：:]\s*(.+)", block)
        location_match = re.search(r"📍\s*勤務地[：:]\s*(.+)", block)

        url = ""
        for code_block in re.findall(r"```[^\n]*\n(.*?)```", block, re.DOTALL):
            candidate = code_block.strip().splitlines()[0].strip() if code_block.strip() else ""
            if candidate.startswith("http"):
                url = candidate

        entries.append({
            "club": title_match.group(1).strip(),
            "role": title_match.group(2).strip(),
            "date": date_match.group(1).strip() if date_match else "",
            "company": company_match.group(1).strip() if company_match else "",
            "employment": employment_match.group(1).strip() if employment_match else "",
            "location": location_match.group(1).strip() if location_match else "",
            "url": url,
        })
    return entries


def sort_key(entry: dict) -> datetime:
    try:
        return datetime.strptime(entry["date"], "%Y/%m/%d")
    except ValueError:
        return datetime.min


def render_card(entry: dict) -> str:
    club = html.escape(entry["club"])
    role = html.escape(entry["role"])
    tags = []
    if entry["employment"]:
        tags.append(html.escape(entry["employment"]))
    if entry["location"]:
        tags.append(html.escape(entry["location"]))
    if entry["company"] and entry["company"] != entry["club"]:
        tags.append(html.escape(entry["company"]))
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    date_html = f'<span class="date">{html.escape(entry["date"])} 掲載</span>' if entry["date"] else ""

    link_html = ""
    if entry["url"]:
        safe_url = html.escape(entry["url"], quote=True)
        link_html = f'<a class="btn" href="{safe_url}" target="_blank" rel="noopener noreferrer">求人を見る →</a>'

    return f"""
    <li class="card">
      <div class="card-head">
        <span class="club">{club}</span>
        {date_html}
      </div>
      <div class="role">{role}</div>
      <div class="tags">{tags_html}</div>
      {link_html}
    </li>"""


def render_html(entries: list[dict], updated_at: str) -> str:
    if entries:
        cards = "\n".join(render_card(e) for e in entries)
        list_html = f'<ul class="cards">{cards}</ul>'
    else:
        list_html = '<p class="empty">現在掲載中の求人はありません。来週の更新をお待ちください。</p>'

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>今週のJリーグ求人｜ジョブサカ</title>
<meta name="description" content="Jリーグクラブのフロントスタッフ求人を毎週自動更新でまとめています。">
<style>
  :root {{
    color-scheme: light dark;
    --bg: #f5f6f8;
    --card-bg: #ffffff;
    --text: #1a1a1a;
    --muted: #6b7280;
    --accent: #0a6b3a;
    --tag-bg: #eef2f0;
    --border: #e5e7eb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #101314;
      --card-bg: #1b1f20;
      --text: #f2f2f2;
      --muted: #9aa1a6;
      --accent: #4ade80;
      --tag-bg: #262b2c;
      --border: #2c3234;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    line-height: 1.6;
  }}
  header {{
    padding: 28px 20px 16px;
    text-align: center;
  }}
  header h1 {{
    margin: 0 0 6px;
    font-size: 1.5rem;
  }}
  header p {{
    margin: 0;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  main {{
    max-width: 640px;
    margin: 0 auto;
    padding: 8px 16px 40px;
  }}
  .cards {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
  }}
  .card-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .club {{
    font-weight: 700;
    color: var(--accent);
    font-size: 0.95rem;
  }}
  .date {{
    font-size: 0.75rem;
    color: var(--muted);
    white-space: nowrap;
  }}
  .role {{
    margin-top: 4px;
    font-size: 1.05rem;
    font-weight: 600;
  }}
  .tags {{
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .tag {{
    background: var(--tag-bg);
    color: var(--muted);
    font-size: 0.75rem;
    padding: 3px 9px;
    border-radius: 999px;
  }}
  .btn {{
    display: inline-block;
    margin-top: 12px;
    padding: 9px 16px;
    border-radius: 999px;
    background: var(--accent);
    color: #062012;
    font-weight: 700;
    font-size: 0.85rem;
    text-decoration: none;
  }}
  .empty {{
    text-align: center;
    color: var(--muted);
    padding: 40px 0;
  }}
  footer {{
    text-align: center;
    padding: 24px 16px 40px;
    color: var(--muted);
    font-size: 0.8rem;
  }}
  footer a {{
    color: var(--muted);
  }}
</style>
</head>
<body>
<header>
  <h1>⚽ 今週のJリーグ求人</h1>
  <p>毎週自動更新・ジョブサカ｜最終更新：{html.escape(updated_at)}</p>
</header>
<main>
  {list_html}
</main>
<footer>
  <p>ジョブサカ｜Jリーグ・スポーツビジネス界への転職を目指す人へ</p>
</footer>
</body>
</html>
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8") if SOURCE.exists() else ""
    entries = parse_entries(text)
    entries.sort(key=sort_key, reverse=True)
    entries = entries[:MAX_ENTRIES]

    updated_at = datetime.now(JST).strftime("%Y年%m月%d日 %H:%M")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_html(entries, updated_at), encoding="utf-8")
    print(f"{len(entries)}件の求人でページを更新しました（{OUTPUT}）")


if __name__ == "__main__":
    main()
