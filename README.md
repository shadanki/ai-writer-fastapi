# LLMO Blog Writer

**LLMO（Large Language Model Optimization）に最適化した記事作成支援システム**です。キーワードから記事のタイトル生成、アウトライン作成、本文生成まで、記事作成の全工程をサポートし、LLMに引用される記事を生成します。

## 🚀 機能

- **セッション管理**: キーワードと下書きの保存・管理
- **タイトル生成**: AIによる5-10件のタイトル案生成とスコアリング
- **アウトライン作成**: 選択したタイトルに基づく構造化されたアウトライン生成
- **本文生成**: アウトラインに基づく記事本文の自動生成
- **Markdown出力**: 完成した記事のMarkdown形式での保存
- **Web UI**: Next.jsとTailwind CSSによるフロントエンド
- **LLMO最適化**: AIの特性を活かしたプロンプトエンジニアリングによる高品質な記事生成

## 🏗️ アーキテクチャ

このプロジェクトは以下の技術スタックで構成されています：

- **バックエンド**: FastAPI (Python)
- **フロントエンド**: Next.js 14 + TypeScript + Tailwind CSS
- **データベース**: SQLite
- **AI**: OpenAI GPT API
- **UIコンポーネント**: Radix UI + shadcn/ui

## 📋 前提条件

- Python 3.8以上
- Node.js 18以上
- pnpm または npm
- OpenAI API キー

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd llmo-blog-writer
```

### 2. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下の内容を設定してください：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./llmoblogwriter.db
EXPORT_DIR=./exports
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. サーバー起動

#### macOS/Linux
```bash
# 実行権限を付与
chmod +x start.sh

# バックエンドサーバー起動（初回は仮想環境と依存関係の自動セットアップ）
./start.sh
```

#### Windows
```bash
# バックエンドサーバー起動（初回は仮想環境と依存関係の自動セットアップ）
start.bat
```

**注意**: 初回実行時は以下の処理が自動で実行されます：
- Python仮想環境の作成
- 依存関係のインストール
- exportsディレクトリの作成

### 4. フロントエンド起動

新しいターミナルを開いて、フロントエンドを起動してください：

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール（初回のみ）
pnpm install
# または
npm install

# 開発サーバーの起動
pnpm dev
# または
npm run dev
```

**重要**: バックエンドとフロントエンドの両方が起動している必要があります。

## 🌐 アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 📱 使用方法

1. **セッション作成**: キーワードを入力してセッションを開始
2. **タイトル生成**: AIが複数のタイトル案を生成
3. **タイトル選択**: 最適なタイトルを選択
4. **アウトライン作成**: 選択したタイトルに基づくアウトラインを生成
5. **本文生成**: アウトラインに従って記事本文を生成
6. **エクスポート**: 完成した記事をMarkdown形式で保存

## 📁 プロジェクト構造

```
llmo-blog-writer/
├── app/                    # FastAPI バックエンド
│   ├── main.py            # メインアプリケーション
│   ├── models.py          # データベースモデル
│   ├── schemas.py         # Pydanticスキーマ
│   ├── services/          # ビジネスロジック
│   └── ...
├── frontend/              # Next.js フロントエンド
│   ├── app/              # App Router
│   ├── components/       # UIコンポーネント
│   └── ...
├── exports/               # 生成された記事の保存先
├── requirements.txt       # Python依存関係
├── start.sh              # 起動スクリプト (macOS/Linux)
└── start.bat             # 起動スクリプト (Windows)
```

## 🔌 API エンドポイント

- `POST /api/session` - セッション作成
- `POST /api/titles` - タイトル生成
- `POST /api/select-title` - タイトル選択
- `POST /api/generate-outline` - アウトライン生成
- `POST /api/generate-article` - 記事本文生成
- `POST /api/export` - 記事エクスポート

## ⚠️ 注意事項

- **httpx バージョン**: このプロジェクトではhttpxのバージョンが0.27.2に固定されています
- **API キー**: OpenAI API キーは必ず`.env`ファイルで管理し、リポジトリにコミットしないでください
- **CORS設定**: フロントエンドとバックエンドの通信のため、適切なCORS設定が必要です

## 🚀 デプロイ

### 本番環境での注意点

- プロンプトとテンプレートの調整
- 出典リンクの一次情報比率の向上
- 構造化データ（JSON-LD）の適切な実装
- セキュリティ設定の強化