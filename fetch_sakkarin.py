"""さっかりんの「求人」トピック（クラブ公式の求人・募集のお知らせ一覧）を取得し、sakkarin_feed.md に書き出す。

ページ本体（topics/info.php?id=176）はEUC-JPで、一覧はJavaScriptで後から読み込まれるため、
読み込み元のXML（UTF-8）を直接取る。jleague-jobs スキルはこのファイルを候補リストとして読む。
"""
from __future__ import annotations

import html
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

FEED_URL = "http://soccer.phew.homeip.net/xml/topics.php?id=176&start=1&size=80"
OUTPUT = Path("sakkarin_feed.md")
# 求人の掲載は数週間続くことが多いので、少し長めに遡る
LOOKBACK_DAYS = 45

ITEM_RE = re.compile(r"<html><!\[CDATA\[(.*?)\]\]></html>", re.DOTALL)


def parse(xml: str) -> list[dict]:
    items = []
    for block in ITEM_RE.findall(xml):
        d = re.search(r"(\d{2})年(\d{2})月(\d{2})日", block)
        club = re.search(r'title="([^"]+)"', block)
        link = re.search(r'<a href="(https?://[^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
        if not (d and link):
            continue
        items.append({
            "date": date(2000 + int(d.group(1)), int(d.group(2)), int(d.group(3))),
            "club": club.group(1) if club else "",
            "title": html.unescape(re.sub(r"<[^>]+>", "", link.group(2))).strip(),
            "url": html.unescape(link.group(1)),
        })
    return items


def main() -> None:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0 (jobsaka-jobs weekly)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml = resp.read().decode("utf-8", errors="replace")
    except Exception as e:  # 取得失敗でも他のソースで収集を続けられるよう、空のファイルを書いて終了する
        OUTPUT.write_text(f"# さっかりん 求人フィード\n\n取得失敗：{e}\n", encoding="utf-8")
        print(f"さっかりんの取得に失敗：{e}", file=sys.stderr)
        return

    since = date.today() - timedelta(days=LOOKBACK_DAYS)
    items = [i for i in parse(xml) if i["date"] >= since]

    lines = [
        "# さっかりん 求人フィード",
        "",
        f"取得元：{FEED_URL}",
        f"直近{LOOKBACK_DAYS}日（{since:%Y/%m/%d}以降）のクラブ公式の求人・募集のお知らせ：{len(items)}件",
        "",
        "| 掲載日 | クラブ | タイトル | URL |",
        "|---|---|---|---|",
    ]
    for i in items:
        title = i["title"].replace("|", "｜")
        lines.append(f"| {i['date']:%Y/%m/%d} | {i['club']} | {title} | {i['url']} |")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(items)}件を {OUTPUT} に書き出し")


if __name__ == "__main__":
    main()
