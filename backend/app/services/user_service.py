"""用户资料、学习记录与个性化推荐服务。"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from bson import ObjectId

from app.database import (
    activities_collection,
    creations_collection,
    favorites_collection,
    poems_collection,
    users_collection,
    wrong_answers_collection,
)
from app.models import CreationRecordRequest, LearningEventRequest, UserProfileUpdate, WrongAnswerRequest


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _poem(doc: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(doc)
    item["id"] = str(item.pop("_id"))
    return item


def _record(doc: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(doc)
    item["id"] = str(item.pop("_id"))
    return item


async def get_profile(username: str) -> Dict[str, Any]:
    doc = await users_collection.find_one({"_id": username}) or {}
    return {
        "username": username,
        "display_name": doc.get("display_name", username),
        "bio": doc.get("bio", ""),
        "role": doc.get("role", "user"),
        "preferred_dynasties": doc.get("preferred_dynasties", []),
        "preferred_genres": doc.get("preferred_genres", []),
        "preferred_tags": doc.get("preferred_tags", []),
        "created_at": doc.get("created_at"),
    }


async def update_profile(username: str, body: UserProfileUpdate) -> Dict[str, Any]:
    values = body.model_dump()
    # 去重并移除空值，防止偏好字段无限膨胀。
    for key in ("preferred_dynasties", "preferred_genres", "preferred_tags"):
        values[key] = list(dict.fromkeys(v.strip() for v in values[key] if v.strip()))
    values["display_name"] = values["display_name"].strip()
    values["bio"] = values["bio"].strip()
    values["updated_at"] = utcnow()
    await users_collection.update_one({"_id": username}, {"$set": values})
    return await get_profile(username)


async def add_favorite(username: str, poem_id: str) -> bool:
    if not await poems_collection.find_one({"_id": poem_id}, {"_id": 1}):
        return False
    await favorites_collection.update_one(
        {"username": username, "poem_id": poem_id},
        {"$setOnInsert": {"created_at": utcnow()}},
        upsert=True,
    )
    return True


async def remove_favorite(username: str, poem_id: str) -> None:
    await favorites_collection.delete_one({"username": username, "poem_id": poem_id})


async def favorite_status(username: str, poem_id: str) -> bool:
    return bool(await favorites_collection.find_one({"username": username, "poem_id": poem_id}, {"_id": 1}))


async def list_favorites(username: str, limit: int = 50) -> List[Dict[str, Any]]:
    refs = []
    async for doc in favorites_collection.find({"username": username}).sort("created_at", -1).limit(limit):
        refs.append(doc["poem_id"])
    if not refs:
        return []
    docs = {}
    async for doc in poems_collection.find({"_id": {"$in": refs}}):
        docs[str(doc["_id"])] = _poem(doc)
    return [docs[poem_id] for poem_id in refs if poem_id in docs]


async def record_view(username: str, poem_id: str) -> bool:
    if not await poems_collection.find_one({"_id": poem_id}, {"_id": 1}):
        return False
    now = utcnow()
    await activities_collection.update_one(
        {"username": username, "event_type": "view", "poem_id": poem_id},
        {
            "$set": {"created_at": now},
            "$inc": {"view_count": 1},
            "$setOnInsert": {"first_viewed_at": now},
        },
        upsert=True,
    )
    return True


async def list_history(username: str, limit: int = 20) -> List[Dict[str, Any]]:
    refs = []
    async for doc in activities_collection.find(
        {"username": username, "event_type": "view"}
    ).sort("created_at", -1).limit(limit):
        refs.append(doc["poem_id"])
    if not refs:
        return []
    docs = {}
    async for doc in poems_collection.find({"_id": {"$in": refs}}):
        docs[str(doc["_id"])] = _poem(doc)
    return [docs[poem_id] for poem_id in refs if poem_id in docs]


async def record_learning_event(username: str, body: LearningEventRequest) -> None:
    await activities_collection.insert_one({
        "username": username,
        "event_type": body.event_type,
        "correct": body.correct,
        "score": body.score,
        "question_type": body.question_type.strip(),
        "source": body.source.strip(),
        "tags": list(dict.fromkeys(body.tags)),
        "created_at": utcnow(),
    })


async def learning_summary(username: str) -> Dict[str, Any]:
    total = correct = score = 0
    quiz_total = chain_total = 0
    recent_correct: List[bool] = []
    weak = Counter()
    cursor = activities_collection.find(
        {"username": username, "event_type": {"$in": ["quiz", "chain"]}}
    ).sort("created_at", -1)
    async for doc in cursor:
        total += 1
        score += int(doc.get("score", 0))
        is_correct = bool(doc.get("correct"))
        correct += int(is_correct)
        quiz_total += int(doc.get("event_type") == "quiz")
        chain_total += int(doc.get("event_type") == "chain")
        if len(recent_correct) < 20:
            recent_correct.append(is_correct)
        if not is_correct and doc.get("question_type"):
            weak[doc["question_type"]] += 1

    streak = 0
    for value in recent_correct:
        if not value:
            break
        streak += 1
    accuracy = round(correct / total * 100, 1) if total else 0
    level = "初识诗意"
    if total >= 30 and accuracy >= 80:
        level = "诗境通达"
    elif total >= 10 and accuracy >= 60:
        level = "渐入佳境"
    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "score": score,
        "quiz_total": quiz_total,
        "chain_total": chain_total,
        "current_streak": streak,
        "level": level,
        "weak_points": [{"type": key, "count": count} for key, count in weak.most_common(5)],
    }


async def save_creation(username: str, body: CreationRecordRequest) -> Dict[str, Any]:
    doc = {
        "username": username,
        **body.model_dump(),
        "created_at": utcnow(),
    }
    result = await creations_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _record(doc)


async def list_creations(username: str, limit: int = 30) -> List[Dict[str, Any]]:
    items = []
    async for doc in creations_collection.find({"username": username}).sort("created_at", -1).limit(limit):
        items.append(_record(doc))
    return items


async def recommendations(username: str, limit: int = 6) -> Dict[str, Any]:
    profile = await get_profile(username)
    signal_tags = Counter(profile["preferred_tags"])
    signal_dynasties = Counter(profile["preferred_dynasties"])
    signal_genres = Counter(profile["preferred_genres"])
    excluded = set()

    source_ids = []
    async for doc in favorites_collection.find({"username": username}).sort("created_at", -1).limit(20):
        source_ids.append(doc["poem_id"])
        excluded.add(doc["poem_id"])
    async for doc in activities_collection.find(
        {"username": username, "event_type": "view"}
    ).sort("created_at", -1).limit(20):
        source_ids.append(doc["poem_id"])
        excluded.add(doc["poem_id"])

    if source_ids:
        async for poem in poems_collection.find({"_id": {"$in": list(set(source_ids))}}):
            signal_tags.update(poem.get("tags") or [])
            if poem.get("dynasty"):
                signal_dynasties[poem["dynasty"]] += 1
            if poem.get("genre"):
                signal_genres[poem["genre"]] += 1

    clauses = []
    if signal_tags:
        clauses.append({"tags": {"$in": [key for key, _ in signal_tags.most_common(8)]}})
    if signal_dynasties:
        clauses.append({"dynasty": {"$in": [key for key, _ in signal_dynasties.most_common(3)]}})
    if signal_genres:
        clauses.append({"genre": {"$in": [key for key, _ in signal_genres.most_common(3)]}})

    query: Dict[str, Any] = {}
    if clauses:
        query["$or"] = clauses
    if excluded:
        query["_id"] = {"$nin": list(excluded)}

    candidates = []
    async for doc in poems_collection.find(query).sort("sort_order", 1).limit(60):
        score = sum(signal_tags[tag] for tag in doc.get("tags") or [])
        score += signal_dynasties[doc.get("dynasty", "")]
        score += signal_genres[doc.get("genre", "")]
        candidates.append((score, _poem(doc)))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return {
        "items": [item for _, item in candidates[:limit]],
        "basis": {
            "tags": [key for key, _ in signal_tags.most_common(5)],
            "dynasties": [key for key, _ in signal_dynasties.most_common(3)],
            "genres": [key for key, _ in signal_genres.most_common(3)],
        },
    }


# ============================================================
#  错题本
# ============================================================

async def add_wrong_answer(username: str, body: WrongAnswerRequest) -> Dict[str, Any]:
    """收录一条错题（含题干与正确答案，供复习）。"""
    doc = {
        "username": username,
        "type": body.type,
        "question": body.question,
        "user_answer": body.user_answer,
        "correct_answer": body.correct_answer,
        "source": body.source,
        "created_at": utcnow(),
    }
    result = await wrong_answers_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _record(doc)


async def list_wrong_answers(username: str, limit: int = 50) -> List[Dict[str, Any]]:
    items = []
    async for doc in wrong_answers_collection.find({"username": username}).sort("created_at", -1).limit(limit):
        items.append(_record(doc))
    return items


async def remove_wrong_answer(username: str, wrong_id: str) -> bool:
    try:
        oid = ObjectId(wrong_id)
    except Exception:
        return False
    result = await wrong_answers_collection.delete_one({"_id": oid, "username": username})
    return result.deleted_count > 0


async def clear_wrong_answers(username: str) -> int:
    result = await wrong_answers_collection.delete_many({"username": username})
    return result.deleted_count


# ============================================================
#  用户画像
# ============================================================

async def portrait(username: str) -> Dict[str, Any]:
    """聚合学习画像：等级/连击 + 兴趣偏好 + 薄弱点 + 近 7 日活跃。"""
    summary = await learning_summary(username)

    # 兴趣偏好：从收藏聚合
    authors: Counter = Counter()
    dynasties: Counter = Counter()
    genres: Counter = Counter()
    tags: Counter = Counter()
    async for fav in favorites_collection.find({"username": username}):
        poem = await poems_collection.find_one({"_id": fav.get("poem_id")})
        if not poem:
            continue
        author = (poem.get("author") or {}).get("name")
        if author:
            authors[author] += 1
        if poem.get("dynasty"):
            dynasties[poem["dynasty"]] += 1
        if poem.get("genre"):
            genres[poem["genre"]] += 1
        for t in poem.get("tags") or []:
            tags[t] += 1

    # 近 7 日活跃
    now = utcnow()
    recent: Counter = Counter()
    async for doc in activities_collection.find(
        {"username": username, "event_type": {"$in": ["quiz", "chain"]}}
    ):
        t = doc.get("created_at")
        if not t:
            continue
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        delta = (now - t).days
        if 0 <= delta < 7:
            recent[delta] += 1
    activity = []
    for d in range(6, -1, -1):
        day = (now - timedelta(days=d)).strftime("%m-%d")
        activity.append({"day": day, "count": recent[d]})

    return {
        "level": summary["level"],
        "streak": summary["current_streak"],
        "stats": {
            "total": summary["total"],
            "correct": summary["correct"],
            "accuracy": summary["accuracy"],
            "score": summary["score"],
        },
        "weak_points": summary["weak_points"],
        "interests": {
            "authors": authors.most_common(5),
            "dynasties": dynasties.most_common(3),
            "genres": genres.most_common(3),
            "tags": tags.most_common(8),
        },
        "recent_activity": activity,
    }
