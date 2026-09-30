"""jleague_jobs.md（X投稿用・時系列）を読み込み、jleague_jobs_by_club.md（クラブ別の蓄積アーカイブ）を更新する。

jleague-jobsスキルは掲載終了した求人を jleague_jobs.md から削除するため、
このスクリプトは「まだ記録されていない求人だけ追記する」追記専用（append-only）で動く。
一度記録した求人は、元の求人情報が消えてもこのファイルには残り続ける。
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

SOURCE = Path("jleague_jobs.md")
OUTPUT = Path("jleague_jobs_by_club.md")
# これより前の日付は旧サイト（jobsoccer.club）から移行した掲載分。
# クラブ採用ページなど使い回しのURLが多く、新着の重複判定に使うと新しい求人を取りこぼすため除外する。
MIGRATED_BEFORE = "2026/08/01"


def parse_source(text: str) -> list[dict]:
    """jleague_jobs.md（時系列ログ）を1求人1dictにパースする。"""
    blocks = re.split(r"\n-{3,}\n", text)
    jobs = []
    for block in blocks:
        block = block.strip()
        title_match = re.search(r"^##\s*(.+?)\s*[|｜]\s*(.+)$", block, re.MULTILINE)
        if not title_match:
            continue

        date_match = re.search(r"取得日時[：:]\s*([\d/]+)", block)
        employment_match = re.search(r"雇用形態[：:]\s*(.+)", block)
        location_match = re.search(r"勤務地[：:]\s*(.+)", block)

        url = ""
        if "返信用URL" in block:
            seg = block[block.find("返信用URL"):]
            url_match = re.search(r"(https?://\S+)", seg)
            if url_match:
                url = url_match.group(1)

        salary = ""
        body_match = re.search(r"X投稿文.*?```\n(.*?)\n```", block, re.DOTALL)
        if body_match:
            sal_lines = [
                line.strip("✅ ").strip()
                for line in body_match.group(1).split("\n")
                if line.strip().startswith("✅")
                and any(kw in line for kw in ("円", "年俸", "月給", "年収"))
            ]
            salary = " / ".join(sal_lines)

        jobs.append({
            "club": title_match.group(1).strip(),
            "title": title_match.group(2).strip(),
            "date": date_match.group(1).strip() if date_match else "",
            "emp": employment_match.group(1).strip() if employment_match else "",
            "loc": location_match.group(1).strip() if location_match else "",
            "salary": salary,
            "url": url,
        })
    return jobs


def parse_archive(text: str) -> list[dict]:
    """既存の jleague_jobs_by_club.md をパースし直す（追記時の重複判定用）。"""
    jobs = []
    for club_match in re.finditer(r"^## ([^\n]+?)（\d+件）\n(.*?)(?=\n## |\Z)", text, re.DOTALL | re.MULTILINE):
        club = club_match.group(1).strip()
        body = club_match.group(2)
        for job_match in re.finditer(r"^### ([\d/]+)｜(.+)$\n((?:- .+\n?)*)", body, re.MULTILINE):
            date, title, fields = job_match.group(1), job_match.group(2).strip(), job_match.group(3)
            emp = re.search(r"- 雇用形態：(.+)", fields)
            loc = re.search(r"- 勤務地：(.+)", fields)
            salary = re.search(r"- 給与：(.+)", fields)
            url = re.search(r"- 求人URL：(.+)", fields)
            jobs.append({
                "club": club,
                "title": title,
                "date": date,
                "emp": emp.group(1).strip() if emp else "",
                "loc": loc.group(1).strip() if loc else "",
                "salary": salary.group(1).strip() if salary else "",
                "url": url.group(1).strip() if url else "",
            })
    return jobs


def job_key(job: dict) -> tuple[str, str]:
    """重複判定キー。URLがあればURL、なければクラブ＋職種＋日付。"""
    if job["url"]:
        return ("url", job["url"])
    return ("noturl", job["club"], job["title"], job["date"])


def render(jobs: list[dict]) -> str:
    by_club: dict[str, list[dict]] = defaultdict(list)
    for job in jobs:
        by_club[job["club"]].append(job)
    for club_jobs in by_club.values():
        club_jobs.sort(key=lambda j: j["date"])

    club_order = sorted(by_club.keys(), key=lambda c: (-len(by_club[c]), by_club[c][0]["date"]))

    lines = ["# Jリーグ求人まとめ（クラブ別）", ""]
    lines.append("元データ：`jleague_jobs.md`（X投稿用・時系列）を再構成した蓄積アーカイブ。")
    lines.append("掲載終了した求人も削除せず残す（追記専用）。`generate_by_club.py` で自動更新。")
    lines.append(f"{MIGRATED_BEFORE}より前の掲載分は旧サイト（jobsoccer.club）のクラブ別記事から移行したもの（2026-09-30）。")
    lines.append("")
    lines.append("## サマリー")
    lines.append("")
    lines.append("| クラブ | 件数 | 初出 | 最新 |")
    lines.append("|---|---|---|---|")
    for club in club_order:
        club_jobs = by_club[club]
        lines.append(f"| {club} | {len(club_jobs)} | {club_jobs[0]['date']} | {club_jobs[-1]['date']} |")
    lines.append("")
    lines.append(f"**合計：{len(jobs)}件（{len(by_club)}クラブ）**")
    lines.append("")
    lines.append("---")
    lines.append("")

    for club in club_order:
        club_jobs = by_club[club]
        lines.append(f"## {club}（{len(club_jobs)}件）")
        lines.append("")
        for job in club_jobs:
            lines.append(f"### {job['date']}｜{job['title']}")
            lines.append(f"- 雇用形態：{job['emp']}")
            lines.append(f"- 勤務地：{job['loc']}")
            if job["salary"]:
                lines.append(f"- 給与：{job['salary']}")
            lines.append(f"- 求人URL：{job['url']}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    source_jobs = parse_source(SOURCE.read_text(encoding="utf-8"))
    archive_jobs = parse_archive(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else []

    known_keys = {job_key(job) for job in archive_jobs if job["date"] >= MIGRATED_BEFORE}
    new_jobs = [job for job in source_jobs if job_key(job) not in known_keys]

    all_jobs = archive_jobs + new_jobs
    OUTPUT.write_text(render(all_jobs), encoding="utf-8")
    print(f"{len(new_jobs)}件を追加（合計{len(all_jobs)}件）")


if __name__ == "__main__":
    main()
