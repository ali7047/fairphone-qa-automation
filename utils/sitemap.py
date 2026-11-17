"""Pick the pages the weekly detection job checks: a small, fair, repeatable sample.

- Reads the shop's sitemap (a list of every public page).
- Leaves out addresses that are not pages for visitors: login/sign-up actions,
  "add to …" actions, and anything robots.txt tells crawlers not to visit.
- Takes at most N pages, spread over the sections of the site (shop, stories,
  legal, …), so one big section can't fill the whole sample.
- Uses a seed, so the same seed gives the same pages: a re-run of a failed
  week checks exactly the same pages. The workflow uses the ISO week as seed,
  so every week a different part of the site gets checked.
"""

from __future__ import annotations

import random
import re
from collections import defaultdict
from urllib.parse import urlparse

_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
_LANGUAGE_PREFIX = re.compile(r"^/(nl|fr|de|en)(?=/|$)")

# Addresses in the sitemap that are actions, not pages a visitor reads.
_NOT_PAGES = re.compile(r"^/(auth0|add|web|my|shop/cart|shop/checkout|shop/address|shop/payment)(/|$)")


def urls_from_sitemap(xml: str) -> list[str]:
    """All page addresses listed in a sitemap file (in order, without duplicates)."""
    return list(dict.fromkeys(_LOC.findall(xml)))


def disallowed_paths(robots_txt: str) -> list[str]:
    """Path prefixes that robots.txt asks every crawler ("User-agent: *") not to visit."""
    paths, applies = [], False
    for raw in robots_txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = (part.strip() for part in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            applies = value == "*"
        elif field == "disallow" and applies and value:
            paths.append(value)
    return paths


def path_of(url: str) -> str:
    return urlparse(url).path or "/"


def section_of(url: str) -> str:
    """The part of the site a page belongs to: "shop", "stories", "legal"; "home" for the home page.

    The language prefix is ignored, so /nl/stories/x and /stories/x are both "stories".
    """
    path = _LANGUAGE_PREFIX.sub("", path_of(url))
    first = path.strip("/").split("/")[0]
    return first or "home"


def is_checkable(url: str, disallowed: list[str], host: str) -> bool:
    """A page we may and should check: on the shop's own host, a real page, allowed by robots.txt."""
    parsed = urlparse(url)
    if parsed.netloc != host:
        return False
    path = parsed.path or "/"
    bare = _LANGUAGE_PREFIX.sub("", path) or "/"
    if _NOT_PAGES.match(bare):
        return False
    return not any(path.startswith(prefix) for prefix in disallowed)


def sample_pages(urls: list[str], size: int, seed: str, always: tuple[str, ...] = ("home",)) -> list[str]:
    """Pick at most `size` pages, spread over sections, the same for the same seed.

    Sections listed in `always` (the home page) are always included. The rest
    are filled round-robin: one page from each section in turn, so small
    sections (warranty, contact) get checked as well as big ones (stories).
    """
    if size <= 0:
        return []
    by_section: dict[str, list[str]] = defaultdict(list)
    for url in urls:
        by_section[section_of(url)].append(url)

    rng = random.Random(seed)
    for pages in by_section.values():
        pages.sort()
        rng.shuffle(pages)
    sections = sorted(by_section)
    rng.shuffle(sections)
    sections.sort(key=lambda name: name not in always)  # "always" sections first, order otherwise random

    picked: list[str] = []
    while len(picked) < size and any(by_section.values()):
        for name in sections:
            if by_section[name] and len(picked) < size:
                picked.append(by_section[name].pop())
    return picked
