"""HTTP layer for the healthcare API.

Refactored from 386 lines of copy-paste to this module. What changed and why is
recorded in REFACTOR_NOTES.md; the short version is that every viewset repeated
the same methods with the same three problems, and those three problems were
bugs rather than style.

  1. Every read method began with `if request.query_params or request.body:
     return 400`. That is not input validation -- it rejects any GET carrying a
     query string, so `GET /api/patients/?page=2` fails, and it rejects any GET
     with a body, which some HTTP clients send by default. Removed entirely.
  2. `update()` read the target primary key from `request.data["id"]` instead
     of the URL, so PUT was wired to the collection route and any caller could
     rewrite any row by guessing an id. The URL now identifies the resource.
  3. The same methods were reimplemented four times over, and the copies had
     drifted apart: AppointmentViewSet.update never checked for a duplicate
     active appointment, so a rule that create enforced was one request away
     from being bypassed.

Scope of this refactor: HTTP concerns only. Business rules that were already
implemented stay implemented, just relocated. No model, migration, or
authentication change is included -- those are separate pieces of work.
"""

from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Appointment, Doctor, MedicalRecord, Patient
from .serializers import (
    AppointmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    """Shared behaviour for the four resources.

    Holds the methods that were copy-pasted per viewset. A subclass that needs
    extra behaviour overrides a hook rather than re-implementing the method.

    Nothing here touches authentication or authorization. That is deliberate
    and it is a real gap: the API currently has neither, which is tracked as
    separate work, and mixing permission changes into a structural refactor
    would make the two indistinguishable in review.
    """

    def get_queryset(self):
        return self.queryset.all()

    def _get_object_or_404(self):
        """Resolve the URL pk to an instance, or raise Http404.

        Centralising this means every resource renders the same 404 body via
        DRF's handler instead of each view hand-building one.
        """
        instance = self.get_queryset().filter(pk=self.kwargs.get("pk")).first()
        if instance is None:
            raise Http404
        self.check_object_permissions(self.request, instance)
        return instance

    def update(self, request, *args, **kwargs):
        """PUT, with the target taken from the URL rather than the body.

        The previous implementation read `request.data["id"]` and was bound to
        the collection route. Two consequences: the URL did not identify the
        resource, and the body's id was a second handle on it, so a caller who
        guessed any id could write to that row.
        """
        instance = self._get_object_or_404()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """PATCH was unreachable before -- it was never bound in urls.py.

        ModelViewSet already implements it and it costs nothing to expose.
        """
        instance = self._get_object_or_404()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Delete, resolved from the URL, returning a bodyless 204.

        The previous version was inconsistent: Appointment returned a bare 204
        while the other three returned 200 with a message. One behaviour now.
        """
        instance = self._get_object_or_404()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UniqueNameMixin:
    """Duplicate-name detection, shared by Doctor and Patient.

    The check was inline in both create() and update() -- four near-identical
    query blocks -- and each one hand-built its own 400 response.

    Scope limit, stated rather than hidden: this is an application-level check,
    not a database guarantee. There is no unique index on name, so two
    concurrent creates can both pass. Closing that needs a UniqueConstraint and
    a migration, which is outside this refactor.
    """

    resource_label = "resource"

    #: Extra serializer fields, besides name, that must also be unique.
    unique_fields = ("name",)

    def _duplicate_error(self, instance=None):
        """Return an error message if a unique field collides, else None.

        `instance` is excluded from the lookup so an update does not collide
        with the row being updated.
        """
        # Read from the raw payload rather than validated_data: a field absent
        # from a PATCH body must not be checked against the database, or every
        # PATCH that omits `name` would look for a row whose name is None.
        data = self.request.data
        for field in self.unique_fields:
            value = data.get(field)
            if value in (None, ""):
                # Not supplied (PATCH) or blank: nothing to compare against.
                continue
            queryset = self.get_queryset().filter(**{field: value})
            if instance is not None:
                queryset = queryset.exclude(pk=instance.pk)
            if queryset.exists():
                if len(self.unique_fields) == 1:
                    return f"Another {self.resource_label} already has this {field}."
                return (
                    f"Another {self.resource_label} already has this "
                    f"{' or '.join(self.unique_fields)}."
                )
        return None

    def create(self, request, *args, **kwargs):
        """Check for collisions, then delegate to ModelViewSet.

        Both checks happen before any write. An earlier draft called
        perform_create() (which saves) before the phone check, so a rejected
        phone left an already-written row behind.
        """
        error = self._duplicate_error()
        if error:
            raise ValidationError({"detail": error})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self._get_object_or_404()
        error = self._duplicate_error(instance)
        if error:
            raise ValidationError({"detail": error})
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self._get_object_or_404()
        error = self._duplicate_error(instance)
        if error:
            raise ValidationError({"detail": error})
        return super().partial_update(request, *args, **kwargs)


class DoctorViewSet(UniqueNameMixin, BaseModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    resource_label = "doctor"


class PatientViewSet(UniqueNameMixin, BaseModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    resource_label = "patient"
    # name and phone both had duplicate checks in the original code.
    unique_fields = ("name", "phone")


class AppointmentViewSet(BaseModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    # No create() override: both appointment business rules moved into
    # AppointmentSerializer.validate(), so they run identically for create,
    # update and partial update. Previously update() was missing the duplicate
    # active-appointment check that create() had, which made the rule
    # enforceable-or-not depending on which verb the caller chose.


class MedicalRecordViewSet(BaseModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    # No create() override. The original rejected a body whose `id` matched an
    # existing record; with the primary key now server-assigned and read-only
    # there is no body id to check, and the check could never mean anything --
    # a primary key is unique by definition.