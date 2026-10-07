from fastapi import APIRouter

from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.model.common import JsonOutModel


class HealthResponse(JsonOutModel):
    is_healthy: bool


class InfoResponse(JsonOutModel):
    app_version: str
    is_auto_connect: bool
    default_server_url: str
    default_server_username: str
    default_server_password: str


def create_health_api(config: AppConfig) -> APIRouter:
    router = APIRouter(prefix="/api/info", tags=["health"])

    @router.get("/health", tags=["health"])
    async def request_health() -> HealthResponse:
        """Health endpoint"""
        return HealthResponse(is_healthy=True)

    @router.get("/settings", tags=["version"])
    async def request_version() -> InfoResponse:
        """Get the currently running version"""
        return InfoResponse(
            app_version=config.app_version,
            is_auto_connect=config.server_enable_auto_connect,
            default_server_url=config.opc_ua_default_server_url,
            default_server_username=config.opc_ua_default_server_username,
            default_server_password=config.opc_ua_default_server_password,
        )

    return router
