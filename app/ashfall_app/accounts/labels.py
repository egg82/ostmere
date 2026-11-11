"""A device's label in the list of an account's devices (api/CONTRACT.txt, "Your devices"): browser and system read from
the user agent when its session is made, nothing more. The user agent itself is not kept. (habits' push/devices.py.)"""

import re

UNKNOWN = "A browser"
# First match wins: the browsers that also say "Chrome" or "Safari" come before them.
BROWSERS = (("Firefox", r"Firefox/|FxiOS/"), ("Edge", r"Edg(e|A|iOS)?/"), ("Opera", r"OPR/|Opera"),
            ("Samsung Internet", r"SamsungBrowser/"), ("Chrome", r"Chrome/|CriOS/"), ("Safari", r"Safari/"))
SYSTEMS = (("Android", r"Android"), ("iPhone", r"iPhone"), ("iPad", r"iPad"), ("ChromeOS", r"CrOS"),
           ("Windows", r"Windows"), ("Mac", r"Macintosh|Mac OS X"), ("Linux", r"Linux"))


def label(user_agent: str) -> str:
    browser = next((n for n, rx in BROWSERS if re.search(rx, user_agent)), None)
    system = next((n for n, rx in SYSTEMS if re.search(rx, user_agent)), None)
    if browser and system:
        return f"{browser} on {system}"
    return browser or system or UNKNOWN
