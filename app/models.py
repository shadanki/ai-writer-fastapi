from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=gen_uuid)
    topic = Column(Text, nullable=False)
    draft = Column(Text, nullable=True)
    language = Column(String, default="ja")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidates = relationship("TitleCandidate", back_populates="project", cascade="all, delete-orphan")
    article = relationship("Article", back_populates="project", uselist=False, cascade="all, delete-orphan")


class TitleCandidate(Base):
    __tablename__ = "title_candidates"
    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"))
    title = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    why = Column(Text, nullable=True)
    raw = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="candidates")


class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), unique=True)
    selected_title = Column(Text, nullable=False)
    outline = Column(JSON, nullable=True)
    markdown = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="article")