#!/bin/bash

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境をアクティベート
echo "仮想環境をアクティベート中..."
source .venv/bin/activate

# 依存関係の確認
echo "依存関係を確認中..."
pip list | grep -E "(fastapi|uvicorn|openai)"

# FastAPIサーバーを起動
echo "FastAPIサーバーを起動中..."
echo "ブラウザで http://localhost:8000/docs にアクセスしてください"
echo "停止するには Ctrl+C を押してください"
echo ""

python -m uvicorn app.main:app --reload --port 8000
