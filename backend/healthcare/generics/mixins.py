from rest_framework import status
from rest_framework.response import Response

BAD_REQUEST = "Error while processing the request."


def _bad_request():
    return Response({"detail": BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


class StrictRequestMixin:
    """Rejects list/retrieve/destroy requests carrying query params or a body.

    deleted_message = None -> destroy returns 204 with no body.
    """

    not_found_message = "Resource not found."
    deleted_message = "Resource has been deleted."

    def _reject_if_dirty(self, request):
        if request.query_params or request.body:
            return _bad_request()
        return None

    def list(self, request, *args, **kwargs):
        return self._reject_if_dirty(request) or super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return self._reject_if_dirty(request) or super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        err = self._reject_if_dirty(request)
        if err:
            return err
        instance = self.get_queryset().filter(pk=kwargs["pk"]).first()
        if instance is None:
            return Response({"detail": self.not_found_message}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        if self.deleted_message is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": self.deleted_message}, status=status.HTTP_200_OK)


class JsonOnlyMixin:
    """Rejects create/update requests with query params or non-JSON content type."""

    def _reject_if_invalid(self, request):
        if request.query_params or request.content_type != "application/json":
            return _bad_request()
        return None


class IdInBodyUpdateMixin(JsonOnlyMixin):
    """PUT with 'id' in body instead of URL; override validate_update() for extra checks."""

    not_found_message = "Resource not found."
    updated_message = "Resource updated."

    def validate_update(self, serializer, instance):
        """Return a Response to short-circuit, or None to proceed."""
        return None

    def update(self, request, *args, **kwargs):
        err = self._reject_if_invalid(request)
        if err:
            return err
        data = request.data
        if not isinstance(data, dict) or "id" not in data:
            return Response({"detail": "'id' is required in the body."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_queryset().filter(pk=data["id"]).first()
        if instance is None:
            return Response({"detail": self.not_found_message}, status=status.HTTP_404_NOT_FOUND)

        payload = {k: v for k, v in data.items() if k != "id"}
        payload["id"] = instance.pk
        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)

        err = self.validate_update(serializer, instance)
        if err:
            return err

        self.perform_update(serializer)
        return Response({"detail": self.updated_message}, status=status.HTTP_200_OK)


class JsonOnlyCreateMixin(JsonOnlyMixin):
    """POST with JSON-only checks; override validate_create() for extra checks.

    created_message = None -> create returns the serialized object.
    """

    created_message = "Resource created."

    def validate_create(self, serializer):
        """Return a Response to short-circuit, or None to proceed."""
        return None

    def create(self, request, *args, **kwargs):
        err = self._reject_if_invalid(request)
        if err:
            return err

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        err = self.validate_create(serializer)
        if err:
            return err

        self.perform_create(serializer)
        body = serializer.data if self.created_message is None else {"detail": self.created_message}
        return Response(body, status=status.HTTP_201_CREATED)


class StrictCrudMixin(StrictRequestMixin, IdInBodyUpdateMixin, JsonOnlyCreateMixin):
    """Convenience bundle: strict list/retrieve/destroy + JSON create + id-in-body update."""