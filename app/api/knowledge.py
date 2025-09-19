from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.db.database import get_db
from app.models.knowledge_article import KnowledgeArticle
from app.schemas.knowledge import (
    KnowledgeArticleCreate, KnowledgeArticleOut, KnowledgeArticleUpdate
)
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.post("", response_model=KnowledgeArticleOut, dependencies=[Depends(require_roles("analyst", "manager"))])
async def create_article(
    data: KnowledgeArticleCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    article = KnowledgeArticle(**data.dict(), created_by=user.id)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@router.get("", response_model=List[KnowledgeArticleOut])
async def list_articles(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(KnowledgeArticle)
    if category:
        stmt = stmt.where(KnowledgeArticle.category == category)
    if search:
        stmt = stmt.where(KnowledgeArticle.content.ilike(f"%{search}%") | KnowledgeArticle.title.ilike(f"%{search}%"))
    result = await db.execute(stmt.order_by(KnowledgeArticle.created_at.desc()))
    return result.scalars().all()

@router.get("/{article_id}", response_model=KnowledgeArticleOut)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar()
    if not article:
        raise HTTPException(404, "Article not found")
    return article

@router.put("/{article_id}", response_model=KnowledgeArticleOut, dependencies=[Depends(require_roles("analyst", "manager"))])
async def update_article(
    article_id: int,
    data: KnowledgeArticleUpdate,
    db: AsyncSession = Depends(get_db),
    
):
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar()
    if not article:
        raise HTTPException(404, "Article not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(article, field, value)
    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/{article_id}", dependencies=[Depends(require_roles("manager", "admin"))])
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
  
    
):
    
    result = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
    article = result.scalar()
    if not article:
        raise HTTPException(404, "Article not found")
    await db.delete(article)
    await db.commit()
    return {"message": "Deleted"}
