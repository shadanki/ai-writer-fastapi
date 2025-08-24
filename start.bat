@echo off
chcp 65001 >nul
echo 🚀 AI-Writer FastAPI サーバーを起動しています...

REM 仮想環境が存在するかチェック
if not exist "venv" (
    echo 📦 仮想環境が見つかりません。作成中...
    python -m venv venv
    echo ✅ 仮想環境を作成しました
)

REM 仮想環境をアクティベート
echo 🔧 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

REM 依存関係をチェック・インストール
echo 📚 依存関係をチェック中...
pip install -r requirements.txt

REM exportsディレクトリが存在しない場合は作成
if not exist "exports" (
    echo 📁 exportsディレクトリを作成中...
    mkdir exports
)

REM 環境変数ファイルの存在チェック
if not exist ".env" (
    echo ⚠️  .envファイルが見つかりません
    echo 📝 .envファイルを作成してください（OPENAI_API_KEY等の設定が必要）
    echo 例：
    echo OPENAI_API_KEY=your_api_key_here
    echo OPENAI_MODEL=gpt-4o-mini
    echo DATABASE_URL=sqlite:///./aiwriter.db
    echo EXPORT_DIR=./exports
    echo CORS_ORIGINS=http://localhost:3000,http://localhost:8080
    pause
    exit /b 1
)

REM サーバー起動
echo 🌐 サーバーを起動中... (http://localhost:8000)
echo 📖 API ドキュメント: http://localhost:8000/docs
echo ⏹️  停止するには Ctrl+C を押してください
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
