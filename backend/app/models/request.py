"""请求模型"""
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """生成请求"""
    prompt: Optional[str] = Field(None, description="自由描述创作需求", examples=["写一首关于秋天思念远方朋友的七言绝句"])
    scene: Optional[str] = Field(None, description="场景", examples=["中秋"])
    emotion: Optional[str] = Field(None, description="情感", examples=["思乡"])
    style: Optional[str] = Field(None, description="风格", examples=["唐诗"])
    images: List[str] = Field(default_factory=list, description="意象列表")
    draft: Optional[str] = Field(None, description="草稿/仿写文本")
    count: int = Field(1, ge=1, le=3, description="生成数量")
    strict: bool = Field(False, description="是否严格遵循格律")


class ValidateRequest(BaseModel):
    """接龙校验请求"""
    current: str = Field(..., description="当前诗句")
    answer: str = Field(..., description="用户答案")


class OptimizeRequest(BaseModel):
    """优化请求"""
    id: str = Field(..., description="诗词 ID")


class ImageGenerateRequest(BaseModel):
    """文生图请求"""
    poem_text: str = Field(..., description="诗词文本", examples=["床前明月光，疑是地上霜。举头望明月，低头思故乡。"])
    title: str = Field("", description="诗词标题", examples=["静夜思"])
    style: str = Field("水墨国风", description="图片风格")


class ImagePoemRequest(BaseModel):
    """图生文请求"""
    image: str = Field(..., description="base64 编码的图片数据")
    style: str = Field("古风", description="诗词风格偏好", examples=["唐诗", "宋词", "古风"])
    emotion: str = Field("", description="情感基调（可选）", examples=["思乡", "闲适", "豪放"])


class ChainHintRequest(BaseModel):
    """飞花令 AI 提示请求"""
    line: str = Field(..., description="当前诗句")
    level: int = Field(1, ge=1, le=3, description="提示级别：1=意境 2=关键字 3=首字")


class ChainAIValidateRequest(BaseModel):
    """飞花令 AI 校验请求"""
    current: str = Field(..., description="当前诗句")
    answer: str = Field(..., description="用户答案")


class ChainAITurnRequest(BaseModel):
    """飞花令 AI 对战请求"""
    current: str = Field(..., description="当前诗句")


class QuizExplainRequest(BaseModel):
    """答题 AI 解析请求"""
    question: Dict[str, Any] = Field(..., description="题目对象")
    user_answer: int = Field(..., description="用户选择的选项索引")


class QuizSummaryRequest(BaseModel):
    """答题 AI 总结请求"""
    results: List[Dict[str, Any]] = Field(..., description="答题记录列表")


class VideoGenerateRequest(BaseModel):
    """文生视频请求"""
    poem_text: str = Field(..., description="诗词文本", examples=["床前明月光，疑是地上霜。举头望明月，低头思故乡。"])
    title: str = Field("", description="诗词标题", examples=["静夜思"])
    style: str = Field("水墨国风", description="视频风格")


class ImageryAnalyzeRequest(BaseModel):
    """意象分析请求"""
    poem_text: str = Field(..., min_length=1, max_length=2000, description="诗词文本")
    title: str = Field("", description="诗词标题")
    author: str = Field("", description="作者")
    poem_id: Optional[str] = Field(None, description="已有诗词 ID（可选）")


class AssistantChatMessage(BaseModel):
    """AI 助手对话消息"""
    role: Literal["user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")


class AssistantChatRequest(BaseModel):
    """AI 助手对话请求"""
    message: str = Field(..., min_length=1, max_length=1000, description="用户消息")
    history: List[AssistantChatMessage] = Field(default_factory=list, description="对话历史")
    session_id: Optional[str] = Field(None, description="会话 ID")
