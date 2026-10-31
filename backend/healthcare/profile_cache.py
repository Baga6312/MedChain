import json
import logging

import redis
from django.conf import settings

from .models import UserProfile


logger = logging.getLogger(__name__)


def _key(user_id):
    return f"medchain:user-profile:{user_id}"


def _build_profile(user):
    profile = UserProfile.objects.filter(user=user).first()
    return {
        "id": user.id,
        "email": user.email or user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": profile.role if profile else ("admin" if user.is_staff else "patient"),
        "phone": profile.phone if profile else "",
        "address": profile.address if profile else "",
        "avatar_url": profile.avatar.url if profile and profile.avatar else "",
    }


def get_profile(user):
    client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        cached = client.get(_key(user.id))
    except redis.RedisError:
        logger.warning("Redis profile lookup failed; falling back to PostgreSQL.")
        cached = None

    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            logger.warning("Invalid cached profile; rebuilding it.")

    profile = _build_profile(user)
    try:
        client.set(_key(user.id), json.dumps(profile))
    except redis.RedisError:
        logger.warning("Redis profile write failed; continuing with PostgreSQL data.")
    return profile


def invalidate_profile(user_id):
    try:
        redis.Redis.from_url(settings.REDIS_URL).delete(_key(user_id))
    except redis.RedisError:
        logger.warning("Redis profile invalidation failed.")
