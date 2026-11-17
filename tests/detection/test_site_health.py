"""Detection job: open each sampled page and record what goes wrong while it loads."""

from __future__ import annotations

from urllib.parse import urlparse

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from utils.evidence import attach_data, attach_screenshot, step
from utils.site_health import (
    FAIL,
    REPORT,
    PageResult,
    classify_console_error,
    classify_page_status,
    classify_resource_status,
    classify_script_error,
)

# Answers that mean "the bot protection answered, not the shop". A finding to
# report and solve with whoever runs the protection - never something to get around.
BOT_PROTECTION_STATUSES = {403, 429, 503}
SETTLE_MS = 3_000  # time after "load" for late scripts to run and fail (see note in the test)


@allure.feature("Site health (detection)")
@pytest.mark.detection
def test_page_loads_without_errors(page: Page, settings: Settings, detection_page: str, detection_sampling: dict):
    """
    Data:     one page from this week's sample of the sitemap (max 30 pages, robots.txt respected).
    Steps:    1. Open the page in a fresh browser and record every answer of 400 or above,
                 every uncaught script error and every console error while it loads.
              2. Sort each finding: FAIL (the shop must act) or REPORT (shown only).
    Expected: no FAIL findings: the page answers below 400, the shop's own scripts don't
              crash, its own scripts and styles load, its server answers no 5xx.
              REPORT findings (third-party tools, missing images, console messages) are
              listed in the report but don't fail the job.
    """
    allure.dynamic.title(urlparse(detection_page).path or "/")
    allure.dynamic.link(detection_page, name="Open the page")
    attach_data("How the pages were picked", detection_sampling)
    shop_host = urlparse(settings.base_url).netloc
    result = PageResult(detection_page)

    def on_response(response):
        if response.request.resource_type != "document" or response.url != detection_page:
            finding = classify_resource_status(response.url, response.status, response.request.resource_type, shop_host)
            if finding:
                result.findings.append(finding)

    page.on("response", on_response)
    page.on(
        "pageerror",
        lambda error: result.findings.append(classify_script_error(error.message, error.stack, shop_host)),
    )
    page.on(
        "console",
        lambda message: (
            result.findings.append(
                classify_console_error(message.text, (message.location or {}).get("url") or None, shop_host)
            )
            if message.type == "error"
            else None
        ),
    )

    with step("1. Open the page and listen for errors"):
        response = page.goto(detection_page, wait_until="load")
        result.status = response.status if response else None
        # Late scripts (consent, analytics, chat) start after "load"; give them a moment to
        # fail so their errors are counted. This is a fixed wait on purpose: there is no
        # event for "all third-party scripts have finished", and this job only observes.
        page.wait_for_timeout(SETTLE_MS)
        attach_screenshot(page, "Page")

    with step("2. Sort the findings"):
        if result.status in BOT_PROTECTION_STATUSES and "fairphone" not in (page.title() or "").lower():
            result.blocked = True
        status_finding = classify_page_status(detection_page, result.status)
        if status_finding:
            result.findings.insert(0, status_finding)
        failures = [f for f in result.findings if f.verdict == FAIL]
        reported = [f for f in result.findings if f.verdict == REPORT]
        attach_data("Findings that FAIL the job", failures)
        attach_data("Findings shown in the report only", reported)
        allure.dynamic.parameter("findings", f"{len(failures)} fail, {len(reported)} report")

    assert not result.blocked, (
        f"Bot protection answered {result.status} instead of the shop for {detection_page}. "
        "This is a finding to solve with the team that runs the protection (allowlist the test runner); "
        "the job does not try to get around it."
    )
    assert not failures, f"Expected no failing findings on {detection_page}, actual {len(failures)}: " + "; ".join(
        f"{f.kind} {f.detail} at {f.url} ({f.reason})" for f in failures
    )
