"""The Web Push services a device's endpoint may name. The server POSTs to whatever endpoint a person subscribes, so only
the browsers' own push services are accepted: Google FCM (Chrome and the Chromium family), Mozilla autopush (Firefox),
Apple (Safari) and Windows WNS (Edge)."""

from urllib.parse import urlsplit

from urllib3.exceptions import LocationParseError
from urllib3.util import parse_url

HOSTS = frozenset({"fcm.googleapis.com"})
# Each of these hands out more than one host under its own domain (WNS's are regional, e.g. wns2-par02p.notify.windows.com).
DOMAINS = (".push.services.mozilla.com", ".push.apple.com", ".notify.windows.com")


def is_push_service(endpoint: str) -> bool:
    """An https URL on one of the push services' hosts, on the default port, with no user info. The host is the one the
    sender connects to (urllib3's, as requests reads it), and an endpoint the two parsers read differently is refused."""
    if "\\" in endpoint:
        return False
    try:
        u = urlsplit(endpoint)
        port = u.port
        sent_to = parse_url(endpoint).host
    except (ValueError, LocationParseError):
        return False
    host = u.hostname or ""
    return (u.scheme == "https" and u.username is None and u.password is None and port in (None, 443)
            and host == sent_to and (host in HOSTS or host.endswith(DOMAINS)))
