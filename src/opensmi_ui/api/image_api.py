from fastapi import APIRouter, Response

from opensmi_ui.image.image_provider import StaticImageProvider


def create_image_api(image_provider: StaticImageProvider) -> APIRouter:
    router = APIRouter(prefix="/api/static", tags=["static"])

    @router.get(
        "/image",
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
    async def return_default_image():
        image = image_provider.provide_image("default")
        return Response(content=image, media_type="image/png")

    @router.get(
        "/image/{image_id}",
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
    async def get_image_for_id(image_id: str):
        image = image_provider.provide_image(image_id)
        return Response(content=image, media_type="image/png")

    @router.get(
        "/image/",
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
    async def return_default_image_2():
        image = image_provider.provide_image("default")
        return Response(content=image, media_type="image/png")

    return router
