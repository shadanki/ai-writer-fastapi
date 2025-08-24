from pydantic import BaseModel, Field
from typing import List, Optional

class CreateSessionReq(BaseModel):
    topic: str
    draft: Optional[str] = None
    language: str = Field(default="ja", pattern=r"^(ja|en)$")

class CreateSessionResp(BaseModel):
    sessionId: str

class TitlesReq(BaseModel):
    sessionId: str
    maxCandidates: int = Field(default=10, ge=5, le=12)

class TitleCandidateOut(BaseModel):
    id: str
    title: str
    intent: Optional[str] = None
    score: Optional[float] = None
    why: Optional[str] = None

class TitlesResp(BaseModel):
    candidates: List[TitleCandidateOut]

class SelectTitleReq(BaseModel):
    sessionId: str
    candidateId: str

class OutlineReq(BaseModel):
    sessionId: str

class H3Block(BaseModel):
    title: str
    h3: list[str]

class H2Block(BaseModel):
    title: str
    h3: list[str]

class H1Block(BaseModel):
    title: str
    h2: list[H2Block]
    keypoints: list[str]

class OutlineJSON(BaseModel):
    intro: str
    h1: list[H1Block]
    outro: str

class OutlineResp(BaseModel):
    outline: OutlineJSON

class GenerateArticleReq(BaseModel):
    sessionId: str
    outline: OutlineJSON | None = None

class GenerateArticleResp(BaseModel):
    markdown: str
    sections: list[str]

class ExportReq(BaseModel):
    sessionId: str

class ExportResp(BaseModel):
    downloadUrl: str | None = None
    filePath: str | None = None