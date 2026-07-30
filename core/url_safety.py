import ipaddress
import socket
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests

from config.settings import get_settings


def validate_public_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Source URLs must use http or https")
    if parsed.username or parsed.password:
        raise ValueError("Source URLs must not contain credentials")
    if get_settings().allow_private_source_urls:
        return url

    hostname = parsed.hostname.lower().rstrip(".")
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise ValueError("Private or local source URLs are not allowed")
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as exc:
        raise ValueError(f"Source URL hostname could not be resolved: {hostname}") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("Private, loopback, link-local, and reserved source URLs are not allowed")
    return url


def safe_public_get(url: str, **kwargs) -> requests.Response:
    """GET a public URL while validating every redirect destination."""
    current = validate_public_url(url)
    for _ in range(4):
        response = requests.get(current, allow_redirects=False, **kwargs)
        if response.status_code not in {301, 302, 303, 307, 308}:
            return response
        location = response.headers.get("Location")
        if not location:
            return response
        current = validate_public_url(urljoin(current, location))
    raise ValueError("Source URL exceeded the safe redirect limit")
