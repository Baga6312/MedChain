import hashlib
import json
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..models import Patient, SessionToken, UserProfile


def _issue_token(user):
    raw_token = secrets.token_urlsafe(32)
    SessionToken.objects.create(
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        user=user,
        expires_at=timezone.now()
        + timedelta(seconds=settings.SESSION_TOKEN_LIFETIME_SECONDS),
    )
    return raw_token


def _error(detail, status=400):
    return JsonResponse({"detail": detail}, status=status)


def _ensure_role_record(user):
    profile, profile_created = UserProfile.objects.get_or_create(
        user=user,
        defaults={"role": UserProfile.Role.PATIENT},
    )
    if profile_created or profile.role == UserProfile.Role.PATIENT:
        Patient.objects.get_or_create(
            user=user,
            defaults={
                "name": f"{user.first_name} {user.last_name}".strip()
                or user.email
                or user.username,
                "phone": profile.phone,
            },
        )


@csrf_exempt
@require_POST
def register(request):
    try:
        data = json.loads(request.body)
    except (TypeError, ValueError):
        return _error("A valid JSON body is required.")

    email = str(data.get("email", "")).strip().lower()
    password_value = data.get("password", "")
    if not email or not password_value:
        return _error("Email and password are required.")

    User = get_user_model()
    if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
        return _error("An account with this email already exists.")

    user = User(
        username=email,
        email=email,
        first_name=str(data.get("first_name", "")).strip(),
        last_name=str(data.get("last_name", "")).strip(),
    )
    try:
        validate_password(password_value, user)
    except ValidationError as error:
        return _error({"password": list(error.messages)})

    with transaction.atomic():
        user.set_password(password_value)
        user.save()
        UserProfile.objects.create(
            user=user,
            phone=str(data.get("phone", "")).strip(),
            address=str(data.get("address", "")).strip(),
        )
        Patient.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}".strip() or email,
            phone=str(data.get("phone", "")).strip(),
        )

    return JsonResponse({"detail": "Account created successfully."}, status=201)


@csrf_exempt
@require_POST
def login(request):
    try:
        data = json.loads(request.body)
    except (TypeError, ValueError):
        return _error("A valid JSON body is required.")

    email = str(data.get("email", "")).strip().lower()
    password_value = data.get("password", "")
    user = authenticate(request, username=email, **{"password": password_value})
    if user is None or not user.is_active:
        return _error("Invalid email or password.", status=401)

    _ensure_role_record(user)
    return JsonResponse({"access": _issue_token(user)})


@csrf_exempt
@require_POST
def google_mobile_login(request):
    try:
        data = json.loads(request.body)
    except (TypeError, ValueError):
        return _error("A valid JSON body is required.")

    id_token_value = data.get("id_token")
    if not isinstance(id_token_value, str) or not id_token_value:
        return _error("A Google ID token is required.")

    from google.auth.transport import requests
    from google.oauth2 import id_token

    try:
        claims = id_token.verify_oauth2_token(
            id_token_value,
            requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError:
        return _error("Google identity verification failed.", status=401)

    email = claims.get("email")
    if not email or not claims.get("email_verified"):
        return _error("A verified Google email is required.", status=401)

    User = get_user_model()
    user, created = User.objects.get_or_create(
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
    from .oauth import _save_google_avatar

    _save_google_avatar(user, claims.get("picture"))
    return JsonResponse({"access": _issue_token(user)})
