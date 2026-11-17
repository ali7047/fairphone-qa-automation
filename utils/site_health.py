"""Site health: what goes wrong while a page loads, and whether it should fail the job.

Two kinds of findings, from the browser's own view of the page:
- HTTP errors: the page itself, or something it loads (image, script, data), answered 400 or above.
- JavaScript errors: a script crashed (uncaught exception) or logged a console error.

Each finding gets a verdict:
- FAIL   - the shop's own problem that a customer notices: the page itself is broken,
           the shop's own script crashed, or one of the shop's own files is missing.
- REPORT - shown in the report, but does not fail the job: third-party tools
           (analytics, chat, consent, experiments), warnings, and known noise.
Rule of thumb: red must mean "Fairphone has to act". Noise that nobody can fix
teaches people to ignore red. See knowledge/decisions.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

FAIL = "fail"
REPORT = "report"

_STACK_URL = re.compile(r"https?://[^\s)'\"]+?(?=:\d+:\d+|\)|\s|$)")


@dataclass(frozen=True)
class Finding:
    kind: str  # "page status", "resource status", "script error", "console error"
    url: str  # where it happened: the page, or the file that failed
    detail: str  # status code or error message
    first_party: bool
    verdict: str
    reason: str


@dataclass
class PageResult:
    page: str
    status: int | None = None
    findings: list[Finding] = field(default_factory=list)
    blocked: bool = False  # bot protection answered instead of the shop

    @property
    def failed(self) -> bool:
        return self.blocked or any(f.verdict == FAIL for f in self.findings)


def is_first_party(url: str, shop_host: str) -> bool:
    """Fairphone's own address (www.fairphone.com, us.fairphone.com, …), not a third-party tool."""
    host = urlparse(url).netloc.lower()
    site = ".".join(shop_host.lower().split(".")[-2:])  # fairphone.com
    return host == site or host.endswith("." + site)


def classify_page_status(page: str, status: int | None) -> Finding | None:
    if status is None:
        return Finding("page status", page, "no answer", True, FAIL, "The page did not answer at all")
    if status >= 400:
        return Finding("page status", page, str(status), True, FAIL, "A page listed in the sitemap is broken")
    return None


def classify_resource_status(url: str, status: int, resource_type: str, shop_host: str) -> Finding | None:
    """Something the page loads (image, script, style, data) answered 400 or above."""
    if status < 400:
        return None
    own = is_first_party(url, shop_host)
    if not own:
        return Finding("resource status", url, f"{status} ({resource_type})", False, REPORT, "Third-party service")
    if status >= 500:
        return Finding("resource status", url, f"{status} ({resource_type})", True, FAIL, "Shop server error")
    if resource_type in ("script", "stylesheet", "document"):
        return Finding(
            "resource status", url, f"{status} ({resource_type})", True, FAIL, "Shop's own script or style missing"
        )
    # Missing images or a data call that answered 4xx: visible as a gap, worth fixing, not an outage.
    return Finding(
        "resource status", url, f"{status} ({resource_type})", True, REPORT, "Shop's own file missing (not critical)"
    )


def script_source(stack: str | None) -> str | None:
    """The address of the script where an error happened: the first address in its stack trace.

    Browsers don't give a "source" for uncaught errors directly, but the stack
    trace lists the script addresses, innermost first.
    """
    match = _STACK_URL.search(stack or "")
    return match.group(0) if match else None


def classify_script_error(message: str, stack: str | None, shop_host: str) -> Finding:
    """An uncaught JavaScript exception on the page.

    Whose script crashed is read from the stack trace. Without a stack (rare) the
    owner is unknown, so it is reported, not failed: red must point at a real
    shop problem, and an unknown one can't be assigned.
    """
    source = script_source(stack)
    if source is None:
        return Finding("script error", "(unknown script)", message, False, REPORT, "Script owner unknown")
    if is_first_party(source, shop_host):
        return Finding("script error", source, message, True, FAIL, "Shop's own script crashed")
    return Finding("script error", source, message, False, REPORT, "Third-party script crashed")


def classify_console_error(message: str, source_url: str | None, shop_host: str) -> Finding:
    """A console.error message. Browsers also log failed downloads here; those are
    already counted as resource findings, so they are reported only once."""
    own = source_url is not None and is_first_party(source_url, shop_host)
    if message.startswith("Failed to load resource"):
        return Finding("console error", source_url or "(page)", message, own, REPORT, "Same as a resource finding")
    if own:
        return Finding("console error", source_url, message, True, REPORT, "Shop's script logged an error")
    return Finding("console error", source_url or "(unknown)", message, False, REPORT, "Third-party script")
