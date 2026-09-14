"""数据模型：Poem, Author, Analysis"""
from typing import Optional, List
from pydantic import BaseModel, Field


class Author(BaseModel):
    """作者信息"""
    name: str = Field(..., description="作者姓名", examples=["李白"])
    dynasty: Optional[str] = Field(None, description="朝代", examples=["唐"])
    brief: Optional[str] = Field(None, description="简介", examples=["唐代浪漫主义诗人"])


class Analysis(BaseModel):
    """赏析信息"""
    translation: Optional[str] = Field(None, description="白话译文")
    appreciation: Optional[str] = Field(None, description="重点赏析")
    cultural: Optional[str] = Field(None, description="文化拓展")


class Poem(BaseModel):
    """诗词实体"""
    id: str = Field(..., description="唯一 ID", examples=["poem-1"])
    title: str = Field(..., description="诗词标题", examples=["静夜思"])
    author: Optional[Author] = Field(None, description="作者信息")
    dynasty: Optional[str] = Field(None, description="朝代", examples=["唐"])
    genre: Optional[str] = Field(None, description="体裁", examples=["五言绝句"])
    content: List[str] = Field(default_factory=list, description="原文按行分割")
    analysis: Optional[Analysis] = Field(None, description="赏析信息")
    tags: List[str] = Field(default_factory=list, description="关键词/意象")

    class Config:
        populate_by_name = True


class PoemInDB(Poem):
    """MongoDB 中的诗词（_id 映射）"""
    pass
