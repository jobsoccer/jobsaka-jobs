# jobsaka-jobs

ジョブサカ「今週のJリーグ求人」ページの自動生成リポジトリ。

## 仕組み

1. GitHub Actions（毎週月・木 7:00 JST）が起動
2. `jleague-jobs` スキル（`.claude/skills/jleague-jobs/`）がIndeed Japan・スポジョバ／スポタビからJリーグクラブのフロントスタッフ求人を収集し、`jleague_jobs.md` を更新（掲載終了分は削除）
3. `generate_page.py` が `jleague_jobs.md` を読み込み、`docs/index.html`（今週のJリーグ求人ページ）を生成
4. `generate_by_club.py` が `jleague_jobs.md` の新規求人だけを `jleague_jobs_by_club.md`（クラブ別の蓄積アーカイブ）に追記。`jleague_jobs.md` から削除された求人もこちらには残る
5. 変更をリポジトリにコミット・push → GitHub Pagesが自動反映

公開URL（GitHub Pages有効化後）: `https://jobsoccer.github.io/jobsaka-jobs/`

LINE公式アカウントのリッチメニューはこのURLを指すだけでよく、リポジトリ側の更新だけで内容が自動的に最新化される。

## 必要な設定（リポジトリ管理者が一度だけ行う）

- ローカルで `claude setup-token` を実行し、Claude Pro/Maxのサブスクリプション経由のOAuthトークンを発行
- `gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo jobsoccer/jobsaka-jobs` で登録（サブスク利用分としてカウントされ、API従量課金は発生しない）
- Settings → Pages → Source: `Deploy from a branch` / Branch: `main` / Folder: `/docs`

## 手動実行

Actionsタブから `今週のJリーグ求人ページ更新` ワークフローを `Run workflow` で即時実行できる。

## ローカルでのページ生成テスト

```bash
python3 generate_page.py
python3 generate_by_club.py
```

`generate_page.py` は `jleague_jobs.md` を読み込み `docs/index.html` を再生成する。
`generate_by_club.py` は `jleague_jobs.md` の中身をクラブ別に振り分け、`jleague_jobs_by_club.md` に未記録の求人だけ追記する（追記専用・既存分は削除しない）。
