# 作業管理ボード（大阪ワークショップ）

- 公開ページ: https://osakaworkboard-del.github.io/workboard/
- データとログイン: Firebase（プロジェクト osaka-workboard）
- `index.html` は `tools/build.py` で `tools/work-board.html` から作る（`python3 tools/build.py tools/work-board.html config.json`）
- `firestore.rules` の `OWNER_EMAIL` は管理者のメールアドレスに置きかえて Firebase に貼り付ける
