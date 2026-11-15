import hashlib
import logging
import time

import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from ..models import SessionToken


logger = logging.getLogger(__name__)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def cache_key(token_hash):
    return f"medchain:session-token:{token_hash}"


class RedisFirstTokenAuthentication(BaseAuthentication):
    keyword = b"Token"

    def authenticate(self, request):
        authorization = get_authorization_header(request).split()
        if not authorization or authorization[0].lower() != self.keyword.lower():
            return None
        if len(authorization) != 2:
            return None

        try:
            raw_token = authorization[1].decode("utf-8")
        except UnicodeDecodeError:
            return None

        token_hash = hash_token(raw_token)
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

        try:
            user_id = redis_client.get(cache_key(token_hash))
        except redis.RedisError:
            logger.warning("Redis token lookup failed; falling back to PostgreSQL.")
            user_id = None

        if user_id is not None:
            user = get_user_model().objects.filter(
                pk=user_id,
                is_active=True,
            ).first()
            if user is not None:
                return user, raw_token
            try:
                redis_client.delete(cache_key(token_hash))
            except redis.RedisError:
                logger.warning("Redis token eviction failed for an invalid user.")

        token = SessionToken.objects.select_related("user").filter(
            token_hash=token_hash,
        ).first()
        if token is None:
            return None

        now = timezone.now()
        if token.expires_at <= now or not token.user.is_active:
            token.delete()
            try:
                redis_client.delete(cache_key(token_hash))
            except redis.RedisError:
                logger.warning("Redis token eviction failed for an expired token.")
            return None

        ttl = max(1, int(token.expires_at.timestamp() - time.time()))
        try:
            redis_client.setex(cache_key(token_hash), ttl, str(token.user_id))
        except redis.RedisError:
            logger.warning("Redis token write failed; continuing with PostgreSQL token.")
        return token.user, raw_token

    def authenticate_header(self, request):
        return "Token"
