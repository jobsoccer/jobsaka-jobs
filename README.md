# jobsaka-jobs

ジョブサカ「今週のJリーグ求人」ページの自動生成リポジトリ。

## 仕組み

1. GitHub Actions（毎週月曜7:00 JST）が起動
2. `jleague-jobs` スキル（`.claude/skills/jleague-jobs/`）がIndeed Japan・スポジョバ／スポタビからJリーグクラブのフロントスタッフ求人を収集し、`jleague_jobs.md` を更新
3. `generate_page.py` が `jleague_jobs.md` を読み込み、`docs/index.html`（今週のJリーグ求人ページ）を生成
4. 変更をリポジトリにコミット・push → GitHub Pagesが自動反映

公開URL（GitHub Pages有効化後）: `https://jobsoccer.github.io/jobsaka-jobs/`

LINE公式アカウントのリッチメニューはこのURLを指すだけでよく、リポジトリ側の更新だけで内容が自動的に最新化される。

## 必要な設定（リポジトリ管理者が一度だけ行う）

- Settings → Secrets and variables → Actions → `ANTHROPIC_API_KEY` を登録
- Settings → Pages → Source: `Deploy from a branch` / Branch: `main` / Folder: `/docs`

## 手動実行

Actionsタブから `今週のJリーグ求人ページ更新` ワークフローを `Run workflow` で即時実行できる。

## ローカルでのページ生成テスト

```bash
python3 generate_page.py
```

`jleague_jobs.md` を読み込み `docs/index.html` を再生成する。
