"""用户学习闭环服务测试。"""
import asyncio

from app.models import UserProfileUpdate
from app.routers.system import _configured
from app.services import user_service


class AsyncCursor:
    def __init__(self, docs):
        self.docs = list(docs)

    def sort(self, *_args):
        return self

    def __aiter__(self):
        self._iter = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class FakeUsers:
    def __init__(self, doc):
        self.doc = doc

    async def find_one(self, _query):
        return self.doc

    async def update_one(self, _query, update):
        self.doc.update(update["$set"])


class FakeActivities:
    def __init__(self, docs):
        self.docs = docs

    def find(self, _query):
        return AsyncCursor(self.docs)


def test_capability_key_detection():
    assert _configured("real-key") is True
    assert _configured("") is False
    assert _configured("your-image-api-key") is False


def test_update_profile_normalizes_preferences(monkeypatch):
    users = FakeUsers({"_id": "tester", "role": "user"})
    monkeypatch.setattr(user_service, "users_collection", users)
    body = UserProfileUpdate(
        display_name="  诗友  ",
        bio="  喜欢唐诗  ",
        preferred_dynasties=["唐", "唐", "宋"],
        preferred_genres=["七言绝句"],
        preferred_tags=["明月", "明月", "山水"],
    )
    result = asyncio.run(user_service.update_profile("tester", body))
    assert result["display_name"] == "诗友"
    assert result["preferred_dynasties"] == ["唐", "宋"]
    assert result["preferred_tags"] == ["明月", "山水"]


def test_learning_summary(monkeypatch):
    docs = [
        {"event_type": "quiz", "correct": True, "score": 10, "question_type": "author"},
        {"event_type": "chain", "correct": True, "score": 10, "question_type": "classic_chain"},
        {"event_type": "quiz", "correct": False, "score": 0, "question_type": "author"},
    ]
    monkeypatch.setattr(user_service, "activities_collection", FakeActivities(docs))
    result = asyncio.run(user_service.learning_summary("tester"))
    assert result["total"] == 3
    assert result["correct"] == 2
    assert result["accuracy"] == 66.7
    assert result["quiz_total"] == 2
    assert result["chain_total"] == 1
    assert result["current_streak"] == 2
    assert result["weak_points"][0] == {"type": "author", "count": 1}
