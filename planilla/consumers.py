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

class ServicioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conectar al WebSocket global de servicios."""
        self.group_name = "servicios"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Salir del grupo al desconectarse."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Manejar mensajes entrantes."""
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "send_servicio_update", "data": data}
        )

    async def send_servicio_update(self, event):
        """Enviar actualización de servicio a los clientes."""
        await self.send(text_data=json.dumps(event["data"]))