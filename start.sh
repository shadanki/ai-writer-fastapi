#!/bin/bash

# AI-Writer FastAPI サーバー起動スクリプト

echo "🚀 AI-Writer FastAPI サーバーを起動しています..."

# 仮想環境が存在するかチェック
if [ ! -d "venv" ]; then
    echo "📦 仮想環境が見つかりません。作成中..."
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
fi

# 仮想環境をアクティベート
echo "🔧 仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係をチェック・インストール
echo "📚 依存関係をチェック中..."
pip install -r requirements.txt

# exportsディレクトリが存在しない場合は作成
if [ ! -d "exports" ]; then
    echo "📁 exportsディレクトリを作成中..."
    mkdir -p exports
fi

# 環境変数ファイルの存在チェック
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません"
    echo "📝 .envファイルを作成してください（OPENAI_API_KEY等の設定が必要）"
    echo "例："
    echo "OPENAI_API_KEY=your_api_key_here"
    echo "OPENAI_MODEL=gpt-4o-mini"
    echo "DATABASE_URL=sqlite:///./aiwriter.db"
    echo "EXPORT_DIR=./exports"
    echo "CORS_ORIGINS=http://localhost:3000,http://localhost:8080"
    exit 1
fi

# サーバー起動
echo "🌐 サーバーを起動中... (http://localhost:8000)"
echo "📖 API ドキュメント: http://localhost:8000/docs"
echo "⏹️  停止するには Ctrl+C を押してください"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
