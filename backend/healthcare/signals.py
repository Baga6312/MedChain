import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .blockchain import anchoring, chain
from .models import TreatmentEvent

log = logging.getLogger(__name__)


def _anchor(event_pk):
    try:
        ev = TreatmentEvent.objects.select_related("block", "treatment_episode").get(pk=event_pk)
        anchoring.anchor_head(ev.treatment_episode, ev.block.chain)
    except Exception:  # never break event creation because the chain service is down
        log.exception("anchoring failed")


@receiver(post_save, sender=TreatmentEvent)
def record_event_on_chain(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        chain.append_event(instance)
        transaction.on_commit(lambda: _anchor(instance.pk))