import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "location_updates"
        # Unir al grupo de WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo cuando se desconecte
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data['latitude']
        longitude = data['longitude']
        speed = data['speed']
        heading = data['heading']

        # Enviar los datos a todos los clientes conectados
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'heading': heading,
            }
        )

    async def location_update(self, event):
        # Recibir la ubicación del grupo y enviarla al cliente
        latitude = event['latitude']
        longitude = event['longitude']
        speed = event['speed']
        heading = event['heading']

        # Enviar la ubicación al WebSocket
        await self.send(text_data=json.dumps({
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'heading': heading,
        }))

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.destacamento = self.scope['url_route']['kwargs'].get('destacamento', 'default')
        self.group_name = f"notificacion_{self.destacamento}"

        print(f"📡 Intentando conectar al grupo: {self.group_name}")  # <-- Debug
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"✅ Conectado a {self.group_name}")  # <-- Debug

    async def disconnect(self, close_code):
        print(f"❌ Desconectando del grupo: {self.group_name}")  # <-- Debug
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"📥 Mensaje recibido: {text_data}")  # <-- Debug
        data = json.loads(text_data)
        mensaje = data.get("mensaje", "Sin mensaje")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "enviar_notificacion",
                "mensaje": mensaje,
            }
        )

    async def enviar_notificacion(self, event):
        mensaje = event["mensaje"]
        print(f"🚀 Enviando mensaje: {mensaje}")  # <-- Debug
        await self.send(text_data=json.dumps({"mensaje": mensaje}))


class ServicioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("servicios", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("servicios", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "finalizar_servicio":
            # Enviar a todos los clientes que un servicio fue eliminado
            await self.channel_layer.group_send(
                "servicios",
                {
                    "type": "servicio_finalizado",
                    "id": data["id"],
                }
            )

    async def servicio_finalizado(self, event):
        await self.send(text_data=json.dumps(event))