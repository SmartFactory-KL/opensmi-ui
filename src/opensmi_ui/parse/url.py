from urllib.parse import urlparse


def validate_url(
    url_input: str,
    schemes: list[str] | None = None,
):
    """Validates a url. If no schemes are specified, it checks [http, https].

    Raises:
       ValueError if not a valid url."""
    if schemes is None:
        schemes = ["http", "https"]

    parsed = urlparse(url=url_input)

    if not parsed.scheme:
        raise ValueError(
            f"URL {url_input!r} has no scheme. Expected one of: {', '.join(schemes)}"
        )

    if parsed.scheme not in schemes:
        raise ValueError(
            f"URL {url_input!r} uses scheme {parsed.scheme!r}, "
            f"but allowed schemes are: {', '.join(schemes)}"
        )

    if not parsed.hostname:
        raise ValueError(f"URL {url_input!r} has no hostname")
