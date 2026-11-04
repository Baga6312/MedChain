import logging
import time
import uuid

from django.conf import settings


logger = logging.getLogger("medchain.http")


def _request_user_id(request):
    user = getattr(request, "user", None)
    return user.pk if user is not None and user.is_authenticated else None


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.request_id = request_id
        started = time.monotonic()
        try:
            response = self.get_response(request)
        except Exception:
            logger.exception(
                "Unhandled request exception",
                extra={
                    "environment": settings.LOG_ENVIRONMENT,
                    "service": settings.LOG_SERVICE_NAME,
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.path,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    "user_id": _request_user_id(request),
                },
            )
            raise

        response["X-Request-ID"] = request_id
        logger.log(
            logging.WARNING if response.status_code >= 500 else (
                logging.INFO if response.status_code < 400 else logging.WARNING
            ),
            "HTTP request completed",
            extra={
                "environment": settings.LOG_ENVIRONMENT,
                "service": settings.LOG_SERVICE_NAME,
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
                "user_id": _request_user_id(request),
            },
        )
        return response
