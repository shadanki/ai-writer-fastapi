# AI-Writer FastAPI Scaffold

## クイックスタート

### 1. 環境設定
```bash
# .envファイルを作成
cp .env.example .env
# または手動で.envファイルを作成し、OPENAI_API_KEY等を設定
```

### 2. サーバー起動
```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

**注意**: このプロジェクトではhttpxのバージョンが0.27.2に固定されています。

### 3. アクセス
- API ドキュメント: http://localhost:8000/docs
- サーバー: http://localhost:8000

## できること
- セッション作成（キーワード/下書き保存）
- タイトル案 5–10件 生成 + 簡易スコア
- タイトル選択 → アウトラインJSON生成
- アウトライン→本文（H2単位）生成 + 最終整形
- Markdown保存（ローカル）

## エンドポイント
- POST /api/session
- POST /api/titles
- POST /api/select-title
- POST /api/generate-outline
- POST /api/generate-article
- POST /api/export

## 注意
- LLMの出力がJSONでない場合のフォールバックを用意
- 本番ではプロンプト/テンプレを調整し、出典リンクの一次情報比率を上げる
- 構造化データ（JSON-LD）はフロントで付与するか、本文末尾に自動追加しても良い