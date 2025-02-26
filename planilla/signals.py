from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Servicio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Servicio)
def servicio_guardado(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    data = {
        "tipo": "nuevo_servicio",
        "servicio": {
            "id": instance.id,
            "numero": instance.numero,
            "tipo": instance.tipo.tipo,
            "estado": instance.estado,
            "direccion": instance.direccion,
            "zona": instance.zona,
            "latitud": instance.latitud,
            "longitud": instance.longitud,
        }
    }

    async_to_sync(channel_layer.group_send)("servicios", {"type": "send_servicio_update", "data": data})

    if instance.estado == "Finalizado":
        async_to_sync(channel_layer.group_send)(
            "servicios", {"type": "servicio_finalizado", "id": instance.id}
        )

