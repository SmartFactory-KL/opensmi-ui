import os

IMAGE_FOLDER = "./static/images/"

image_dict: dict[str, bytes] = {}


def provider_load_images():
    for entry in os.scandir(IMAGE_FOLDER):
        if entry.is_file() and entry.name.endswith(".png"):
            with open(entry.path, "rb") as image_file:
                image_dict[entry.name.replace(".png", "")] = image_file.read()


def provider_get_image(image_id: str) -> bytes:
    image_path = "default"

    if image_id.endswith(".png"):
        image_id = image_id.replace(".png", "")

    if image_id in image_dict:
        image_path = image_id

    return image_dict[image_path]
