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
    initial = html.escape(entry["club"][:1]) if entry["club"] else "⚽"
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
        link_html = f'<a class="btn" href="{safe_url}" target="_blank" rel="noopener noreferrer">求人を見る<span class="btn-arrow" aria-hidden="true">→</span></a>'

    return f"""
    <li class="card">
      <div class="card-head">
        <span class="badge" aria-hidden="true">{initial}</span>
        <div class="card-head-text">
          <span class="club">{club}</span>
          {date_html}
        </div>
      </div>
      <h2 class="role">{role}</h2>
      <div class="tags">{tags_html}</div>
      {link_html}
    </li>"""


def render_html(entries: list[dict], updated_at: str) -> str:
    count = len(entries)
    if entries:
        cards = "\n".join(render_card(e) for e in entries)
        list_html = f'<ul class="cards">{cards}</ul>'
    else:
        list_html = (
            '<div class="empty">'
            '<div class="empty-icon">⚽</div>'
            '<p>現在掲載中の求人はありません。<br>来週の更新をお待ちください。</p>'
            '</div>'
        )
    count_badge = (
        f'<span class="count"><strong>{count}</strong> 件掲載中</span>' if entries else ""
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>今週のJリーグ求人｜ジョブサカ</title>
<meta name="description" content="Jリーグクラブのフロントスタッフ求人を毎週自動更新でまとめています。">
<meta property="og:title" content="今週のJリーグ求人｜ジョブサカ">
<meta property="og:description" content="Jリーグクラブのフロントスタッフ求人を毎週自動更新でまとめています。">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  :root {{
    color-scheme: light dark;
    --bg: #eef1ee;
    --card-bg: #ffffff;
    --text: #14201a;
    --muted: #667a70;
    --accent: #0a7a41;
    --accent-2: #16b45f;
    --accent-ink: #ffffff;
    --tag-bg: #eaf3ee;
    --tag-text: #3c6b52;
    --border: #e4e9e5;
    --shadow: 0 6px 22px rgba(16, 54, 34, 0.08);
    --shadow-hover: 0 14px 34px rgba(16, 54, 34, 0.16);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0d1210;
      --card-bg: #161d19;
      --text: #eef3ef;
      --muted: #8fa398;
      --accent: #2ecc71;
      --accent-2: #34e07f;
      --accent-ink: #05130b;
      --tag-bg: #1e2823;
      --tag-text: #8fd6ab;
      --border: #26312b;
      --shadow: 0 6px 22px rgba(0, 0, 0, 0.4);
      --shadow-hover: 0 14px 34px rgba(0, 0, 0, 0.55);
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: "Zen Kaku Gothic New", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }}

  /* ===== Hero ===== */
  .hero {{
    position: relative;
    overflow: hidden;
    padding: 52px 20px 64px;
    text-align: center;
    color: #fff;
    background:
      radial-gradient(1200px 260px at 50% -60px, rgba(255,255,255,0.18), transparent 70%),
      linear-gradient(135deg, #063d23 0%, #0a7a41 55%, #12a555 100%);
  }}
  .hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
      90deg,
      rgba(255,255,255,0.05) 0 40px,
      rgba(255,255,255,0) 40px 80px
    );
    pointer-events: none;
  }}
  .hero::after {{
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: -1px;
    height: 34px;
    background: var(--bg);
    border-radius: 50% 50% 0 0 / 100% 100% 0 0;
  }}
  .hero-inner {{ position: relative; z-index: 1; }}
  .brand {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.28);
    backdrop-filter: blur(4px);
  }}
  .hero h1 {{
    margin: 18px 0 10px;
    font-size: clamp(1.7rem, 6vw, 2.4rem);
    font-weight: 900;
    letter-spacing: 0.01em;
    line-height: 1.25;
  }}
  .hero .sub {{
    margin: 0 auto;
    max-width: 30em;
    font-size: 0.9rem;
    color: rgba(255,255,255,0.86);
  }}
  .hero-meta {{
    margin-top: 20px;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }}
  .count {{
    display: inline-flex;
    align-items: baseline;
    gap: 5px;
    padding: 7px 16px;
    border-radius: 999px;
    background: #fff;
    color: var(--accent);
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
  }}
  .count strong {{
    font-family: "Montserrat", sans-serif;
    font-size: 1.15rem;
    line-height: 1;
  }}
  .updated {{
    font-size: 0.76rem;
    color: rgba(255,255,255,0.8);
  }}

  /* ===== Layout ===== */
  main {{
    max-width: 660px;
    margin: 0 auto;
    padding: 6px 16px 20px;
  }}
  .cards {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  /* ===== Card ===== */
  .card {{
    position: relative;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px 20px 20px 24px;
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  }}
  .card::before {{
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 5px;
    background: linear-gradient(180deg, var(--accent-2), var(--accent));
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
    border-color: color-mix(in srgb, var(--accent) 40%, var(--border));
  }}
  .card-head {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .badge {{
    flex: none;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-weight: 900;
    font-size: 1.2rem;
    color: var(--accent-ink);
    background: linear-gradient(135deg, var(--accent-2), var(--accent));
    box-shadow: 0 4px 12px rgba(10, 122, 65, 0.28);
  }}
  .card-head-text {{
    min-width: 0;
    display: flex;
    flex-direction: column;
  }}
  .club {{
    font-weight: 700;
    color: var(--accent);
    font-size: 0.92rem;
  }}
  .date {{
    font-size: 0.74rem;
    color: var(--muted);
  }}
  .role {{
    margin: 14px 0 0;
    font-size: 1.12rem;
    font-weight: 700;
    line-height: 1.45;
    letter-spacing: 0.005em;
  }}
  .tags {{
    margin-top: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
  }}
  .tag {{
    background: var(--tag-bg);
    color: var(--tag-text);
    font-size: 0.75rem;
    font-weight: 500;
    padding: 4px 11px;
    border-radius: 999px;
  }}
  .btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 16px;
    padding: 10px 20px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent-2), var(--accent));
    color: var(--accent-ink);
    font-weight: 700;
    font-size: 0.86rem;
    text-decoration: none;
    box-shadow: 0 6px 16px rgba(10, 122, 65, 0.26);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .btn:hover {{
    transform: translateY(-1px);
    box-shadow: 0 10px 22px rgba(10, 122, 65, 0.34);
  }}
  .btn-arrow {{ transition: transform 0.15s ease; }}
  .btn:hover .btn-arrow {{ transform: translateX(3px); }}

  /* ===== Empty ===== */
  .empty {{
    text-align: center;
    color: var(--muted);
    padding: 48px 20px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: var(--shadow);
  }}
  .empty-icon {{ font-size: 2.4rem; margin-bottom: 8px; }}
  .empty p {{ margin: 0; }}

  /* ===== Footer ===== */
  footer {{
    text-align: center;
    padding: 8px 16px 48px;
    color: var(--muted);
    font-size: 0.8rem;
  }}
  .footer-brand {{
    font-weight: 700;
    color: var(--text);
  }}
  .footer-tagline {{ margin: 4px 0 0; }}

  @media (prefers-reduced-motion: reduce) {{
    * {{ transition: none !important; }}
  }}
</style>
</head>
<body>
<header class="hero">
  <div class="hero-inner">
    <span class="brand">⚽ ジョブサカ</span>
    <h1>今週のJリーグ求人</h1>
    <p class="sub">Jリーグクラブのフロントスタッフ求人を、毎週自動でまとめてお届けします。</p>
    <div class="hero-meta">
      {count_badge}
      <span class="updated">最終更新：{html.escape(updated_at)}</span>
    </div>
  </div>
</header>
<main>
  {list_html}
</main>
<footer>
  <p class="footer-brand">ジョブサカ</p>
  <p class="footer-tagline">Jリーグ・スポーツビジネス界への転職を目指すすべての人へ</p>
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
