from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Protocol

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from starlette.staticfiles import StaticFiles

from opensmi_ui.api.app_info_api import create_health_api
from opensmi_ui.api.image_api import create_image_api
from opensmi_ui.api.opc_client_api import create_opc_client_api
from opensmi_ui.api.pin_guard_api import create_ping_guard_api
from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.image.image_provider import StaticImageProvider
from opensmi_ui.logger import get_module_logger
from opensmi_ui.messages.broadcast import MessageBroadcaster
from opensmi_ui.messages.funnel import MessageFunnel
from opensmi_ui.messages.receiver import MessageReceiver
from opensmi_ui.metrics.metrics import Metrics
from opensmi_ui.opc_client.client import OPCClient, OPCClientSettings
from opensmi_ui.pin_guard.pin_guard import PinGuard, PinGuardConfig

logger = get_module_logger("composer")


class ComposerInitError(Exception):
    """Raised whenever the init goes wrong"""


class Closable(Protocol):
    async def close(self) -> None: ...


class Startable(Protocol):
    async def start(self) -> None: ...


class Composer:
    def __init__(self):
        self.startables: list[Startable] = []
        self.closables: list[Closable] = []

        self.apis: list[APIRouter] = []

    def compose_application(self, config: AppConfig) -> FastAPI:
        """this initializes and composes all modules but does not start the server yet"""
        try:
            # image provider
            img_provider = StaticImageProvider()
            img_provider.init_module()

            # stats ticker
            app_metrics = Metrics(tick_delay=timedelta(seconds=60))
            self.startables.append(app_metrics)
            self.closables.append(app_metrics)

            # pin guard
            pin_guard = PinGuard(
                PinGuardConfig(
                    autolock_delay=timedelta(
                        seconds=config.pin_guard_autolock_delay_seconds
                    ),
                    is_enabled=config.pin_guard_enabled,
                    pin=str(config.pin_guard_pin),
                )
            )
            self.startables.append(pin_guard)
            self.closables.append(pin_guard)

            pin_guard_api = create_ping_guard_api(pin_guard=pin_guard)
            self.apis.append(pin_guard_api)

            # image api
            img_api = create_image_api(img_provider)
            self.apis.append(img_api)

            # health api
            health_api = create_health_api(config)
            self.apis.append(health_api)

            # message broadcaster/funnel/receiver
            msg_broadcaster = MessageBroadcaster()
            msg_funnel = MessageFunnel(broadcaster=msg_broadcaster)
            msg_funnel.enable_batching_task()

            msg_receiver = MessageReceiver(funnel=msg_funnel)

            # session
            opc_client = OPCClient(
                settings=OPCClientSettings(), msg_receiver=msg_receiver
            )
            self.closables.append(opc_client)

            # session api
            opc_client_api = create_opc_client_api(opc_client=opc_client)
            self.apis.append(opc_client_api)

            # define lifecycle
            @asynccontextmanager
            async def lifespan(app: FastAPI):
                for startable in self.startables:
                    await startable.start()

                yield

                for closable in self.closables:
                    await closable.close()

            # create the actual fastapi application
            app = FastAPI(
                title="OpenSMI UI", version=config.app_version, lifespan=lifespan
            )

            for api_to_append in self.apis:
                app.include_router(api_to_append)

            @app.websocket("/socket")
            async def websocket_endpoint(websocket: WebSocket):
                await msg_broadcaster.connect(websocket)
                # await message_socket.send_refresh_message(websocket)
                try:
                    while True:
                        data = await websocket.receive_json()
                        await websocket.send_json(data)
                except WebSocketDisconnect:
                    await msg_broadcaster.disconnect(websocket=websocket)

            app.mount("/", StaticFiles(directory="public", html=True), name="frontend")

            return app
        except Exception as e:
            raise ComposerInitError(e) from e
