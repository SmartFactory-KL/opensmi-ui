from fastapi import WebSocket

from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.types import WebSocketMessage, WebSocketMessageBatch

logger = get_module_logger("messages.broadcaster")


class MessageBroadcaster:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Called when a new connection is added to the list"""
        await websocket.accept()
        self.active_connections.append(websocket)

        refresh_message = WebSocketMessage(channel="refresh", data=None)
        await websocket.send_text(refresh_message.model_dump_json(by_alias=True))

        logger.info(f"WS connected: {websocket}")

    async def disconnect(self, websocket: WebSocket):
        """Remove a no longer active connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WS disconnected: {websocket}")

    async def remove_connections(self, connections_to_remove: list[WebSocket]):
        if len(connections_to_remove) > 0:
            for connection_to_remove in connections_to_remove:
                await self.disconnect(connection_to_remove)

                try:
                    await connection_to_remove.close()
                except ValueError as _:
                    # Exception is ignored as the connection might have been gone already
                    # which would be raised as value error
                    pass

    async def broadcast(self, message: WebSocketMessage):
        """broadcast a simple WebSocketMessage to all clients"""
        try:
            payload = message.model_dump_json(by_alias=True)
            await self._broadcast_payload(payload)
        except Exception as e:  # noqa: BLE001 # unknown exceptions in broadcast and model_dump
            logger.warning(f"Failed to broadcast: {e}")

    async def broadcast_batch(self, message_batch: list[WebSocketMessage]):
        """broadcast a batch of WebSocketMessages to the batch channel of all clients"""
        batch = WebSocketMessageBatch(channel="batch", data=message_batch)
        payload = batch.model_dump_json(by_alias=True)
        await self._broadcast_payload(payload)

    async def _broadcast_payload(self, payload: str):
        dead_connections: list[WebSocket] = []
        # operates on a snapshot of connections
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:  # noqa: BLE001 Disabled as all exceptions would result in the removal of the connection
                logger.warning(f"Failed to broadcast Payload! Cause: {e}")
                # Payload might be huge batch, would overflow log/console
                # logger.warning(payload)

                dead_connections.append(connection)

        if len(dead_connections) > 0:
            await self.remove_connections(dead_connections)
