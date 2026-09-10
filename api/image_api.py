from fastapi import APIRouter, Response

from static.image_provider import provider_get_image


router = APIRouter(prefix="/api/static", tags=["static"])


@router.get(
    "/image", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def return_default_image():
    image = provider_get_image("default")
    return Response(content=image, media_type="image/png")


@router.get(
    "/image/{image_id}",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_image_for_id(image_id: str):
    image = provider_get_image(image_id)
    return Response(content=image, media_type="image/png")


@router.get(
    "/image/", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def return_default_image_2():
    image = provider_get_image("default")
    return Response(content=image, media_type="image/png")
