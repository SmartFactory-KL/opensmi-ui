from fastapi import APIRouter

from opensmi_ui.app_config.config import AppConfig
from opensmi_ui.model.common import JsonOutModel


class HealthResponse(JsonOutModel):
    is_healthy: bool


def create_health_api(config: AppConfig) -> APIRouter:
    router = APIRouter(prefix="/api/info", tags=["health"])

    @router.get("/health", tags=["health"])
    async def request_health() -> HealthResponse:
        """Health endpoint"""
        return HealthResponse(is_healthy=True)

    @router.get("/version", tags=["version"])
    async def request_version() -> str:
        """Get the currently running version"""
        return config.app_version

    return router
