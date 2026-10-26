import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_GET
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.authtoken.models import Token


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

    token, _ = Token.objects.get_or_create(user=user)
    callback_url = f"{settings.FRONTEND_OAUTH_CALLBACK_URL}#access={urllib.parse.quote(token.key)}"
    return HttpResponseRedirect(callback_url)
