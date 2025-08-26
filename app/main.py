from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, SessionLocal
from .models import Project, Article, TitleCandidate
from .schemas import (
    CreateSessionReq, CreateSessionResp, TitlesReq, TitlesResp, TitleCandidateOut,
    SelectTitleReq, OutlineReq, OutlineResp, GenerateArticleReq, GenerateArticleResp,
    ExportReq, ExportResp,
)
from .services.generation import generate_titles, select_title, generate_outline, generate_article
from .services.exporter import save_markdown_locally
app = FastAPI(title="AI-Writer API", version="0.1.0")

# ルートにアクセスしたら API の情報を返す
@app.get("/")
def root():
    return {"message": "AI-Writer API", "version": "0.1.0"}

# DB初期化
Base.metadata.create_all(bind=engine)

# CORS
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/session", response_model=CreateSessionResp)
def create_session(req: CreateSessionReq, db: Session = Depends(get_db)):
    prj = Project(topic=req.topic.strip(), draft=(req.draft or None), language=req.language)
    db.add(prj)
    db.commit()
    return {"sessionId": prj.id}


@app.post("/api/titles", response_model=TitlesResp)
def api_titles(req: TitlesReq, db: Session = Depends(get_db)):
    try:
        cands = generate_titles(db, req.sessionId, req.maxCandidates)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"candidates": [TitleCandidateOut(**c) for c in cands]}


@app.post("/api/select-title")
def api_select_title(req: SelectTitleReq, db: Session = Depends(get_db)):
    try:
        art = select_title(db, req.sessionId, req.candidateId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "articleId": art.id}


@app.post("/api/generate-outline", response_model=OutlineResp)
def api_generate_outline(req: OutlineReq, db: Session = Depends(get_db)):
    try:
        outline = generate_outline(db, req.sessionId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"outline": outline}


@app.post("/api/generate-article", response_model=GenerateArticleResp)
def api_generate_article(req: GenerateArticleReq, db: Session = Depends(get_db)):
    try:
        markdown, sections = generate_article(db, req.sessionId, req.outline.model_dump() if req.outline else None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"markdown": markdown, "sections": sections}


@app.post("/api/export", response_model=ExportResp)
def api_export(req: ExportReq, db: Session = Depends(get_db)):
    art = db.query(Article).join(Project).filter(Project.id == req.sessionId).first()
    if not art or not art.markdown:
        raise HTTPException(status_code=400, detail="No article to export")

    # 記事のタイトルを先頭に追加
    title_header = f"タイトル：{art.selected_title}\n\n"
    
    # ```markdownと```を除去
    cleaned_markdown = art.markdown.replace("```markdown", "").replace("```", "")
    
    markdown_with_title = title_header + cleaned_markdown

    filename = f"{art.id}.md"
    path = save_markdown_locally(filename, markdown_with_title)
    return {"filePath": path}