import os
from pathlib import Path

IMAGE_FOLDER = "./static/images/"
COMMON_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".avif",
}


class MissingDefaultImageError(Exception):
    """Raised whenever a default image is not set"""


class StaticImageProvider:
    def __init__(self):
        self.images: dict[str, Path] = {}
        self.cache: dict[str, bytes] = {}

    def init_module(self):
        for entry in os.scandir(IMAGE_FOLDER):
            if entry.is_file():
                # only read image files
                ext = self.get_image_extension(entry.name)
                if ext == "":
                    continue

                # try opening it. if that works, save the path.
                with open(entry.path, "rb"):
                    self.images[entry.name.removesuffix(ext)] = Path(entry.path)

        # At least the default image must be present
        if "default" not in self.images:
            raise MissingDefaultImageError(
                "Image provider needs at least one default image"
            )

    def get_image_extension(self, path: str) -> str:
        suffix = Path(path).suffix
        if suffix.lower() in COMMON_IMAGE_EXTENSIONS:
            return suffix
        return ""

    def provide_image(self, image_id: str) -> bytes:
        if not image_id:
            image_id = "default"

        ext = self.get_image_extension(image_id)
        if ext != "":
            image_id = image_id.removesuffix(ext)

        if image_id not in self.images:
            image_id = "default"

        if image_id in self.cache:
            return self.cache[image_id]

        if image_id in self.images:
            path = self.images[image_id]

            with open(path, "rb") as image_file:
                content = image_file.read()
                self.cache[image_id] = content
                return content

        raise MissingDefaultImageError(
            "Providing an image resulted in a catch-all, therefore the default image must be missing"
        )
