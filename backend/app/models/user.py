"""用户学习数据模型。"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    display_name: str = Field("", max_length=32)
    bio: str = Field("", max_length=200)
    preferred_dynasties: List[str] = Field(default_factory=list, max_length=10)
    preferred_genres: List[str] = Field(default_factory=list, max_length=10)
    preferred_tags: List[str] = Field(default_factory=list, max_length=20)


class LearningEventRequest(BaseModel):
    event_type: Literal["quiz", "chain"]
    correct: bool
    score: int = Field(0, ge=0, le=100)
    question_type: str = Field("", max_length=32)
    source: str = Field("", max_length=120)
    tags: List[str] = Field(default_factory=list, max_length=10)


class CreationRecordRequest(BaseModel):
    creation_type: Literal["poem", "mimic", "image", "video"]
    title: str = Field("", max_length=100)
    content: List[str] = Field(default_factory=list, max_length=20)
    asset_url: Optional[str] = Field(None, max_length=2000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=64)
    new_password: str = Field(..., min_length=8, max_length=64)


class WrongAnswerRequest(BaseModel):
    type: str = Field("quiz", max_length=16)
    question: str = Field("", max_length=500)
    user_answer: str = Field("", max_length=200)
    correct_answer: str = Field("", max_length=200)
    source: str = Field("", max_length=120)
