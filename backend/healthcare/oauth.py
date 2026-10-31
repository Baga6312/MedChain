import json
import hashlib
import logging
import secrets
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core import signing
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_GET
from google.auth.transport import requests
from google.oauth2 import id_token
from django.utils import timezone
from datetime import timedelta

from .auth_views import _ensure_role_record
from .models import SessionToken, UserProfile
from .profile_cache import invalidate_profile


logger = logging.getLogger(__name__)


GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH_STATE_SESSION_KEY = "google_oauth_state"


def _configuration_error():
    return JsonResponse(
        {"detail": "Google OAuth is not configured on the backend."},
        status=500,
    )


@require_GET
def google_login(request):
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return _configuration_error()

    state = signing.dumps(secrets.token_urlsafe(32))
    request.session[OAUTH_STATE_SESSION_KEY] = state
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "state": state,
        "prompt": "select_account",
    }
    return HttpResponseRedirect(
        f"{GOOGLE_AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
    )


def _exchange_code(code):
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode()
    request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None


def _save_google_avatar(user, picture_url):
    parsed_url = urllib.parse.urlsplit(str(picture_url or ""))
    hostname = (parsed_url.hostname or "").lower()
    if (
        parsed_url.scheme != "https"
        or not hostname
        or not (
            hostname == "googleusercontent.com"
            or hostname.endswith(".googleusercontent.com")
        )
    ):
        return
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.avatar:
        return
    request = urllib.request.Request(
        picture_url,
        headers={"User-Agent": "MedChain/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")
            image_data = response.read()
        if not content_type.startswith("image/") or not image_data:
            logger.warning("Google avatar response was not a valid image for user %s.", user.pk)
            return
        profile.avatar.save(
            f"google-{user.pk}.jpg",
            ContentFile(image_data),
            save=True,
        )
        invalidate_profile(user.pk)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        logger.warning("Could not download Google avatar for user %s.", user.pk)


@require_GET
def google_callback(request):
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        return _configuration_error()

    expected_state = request.session.pop(OAUTH_STATE_SESSION_KEY, None)
    if not expected_state or not secrets.compare_digest(
        expected_state, request.GET.get("state", "")
    ):
        return HttpResponseBadRequest("Invalid OAuth state.")

    code = request.GET.get("code")
    if not code:
        return HttpResponseBadRequest("Google did not return an authorization code.")

    token_response = _exchange_code(code)
    if not token_response or "id_token" not in token_response:
        return HttpResponseBadRequest("Could not exchange the Google authorization code.")

    try:
        claims = id_token.verify_oauth2_token(
            token_response["id_token"],
            requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError:
        return HttpResponseBadRequest("Google identity verification failed.")

    email = claims.get("email")
    if not email or not claims.get("email_verified"):
        return HttpResponseBadRequest("A verified Google email is required.")

    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(
        username=email,
        defaults={
            "email": email,
            "first_name": claims.get("given_name", ""),
            "last_name": claims.get("family_name", ""),
        },
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])

    _ensure_role_record(user)
    _save_google_avatar(user, claims.get("picture"))

    raw_token = secrets.token_urlsafe(32)
    SessionToken.objects.create(
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        user=user,
        expires_at=timezone.now()
        + timedelta(seconds=settings.SESSION_TOKEN_LIFETIME_SECONDS),
    )
    callback_url = (
        f"{settings.FRONTEND_OAUTH_CALLBACK_URL}"
        f"#access={urllib.parse.quote(raw_token)}"
    )
    return HttpResponseRedirect(callback_url)
