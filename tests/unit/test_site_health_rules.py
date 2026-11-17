"""Unit tests for utils/site_health.py: which findings fail the detection job (no browser).

Why: these rules decide when the weekly job turns red. They are business rules
("red must mean Fairphone has to act"), so they are tested like any other rule.
"""

import pytest

from utils.site_health import (
    FAIL,
    REPORT,
    PageResult,
    classify_console_error,
    classify_page_status,
    classify_resource_status,
    classify_script_error,
    is_first_party,
    script_source,
)

SHOP = "www.fairphone.com"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.fairphone.com/shop/cart", True),
        ("https://fairphone.com/x", True),
        ("https://us.fairphone.com/x", True),
        ("https://support.fairphone.com/hc", True),
        ("https://www.googletagmanager.com/gtm.js", False),
        ("https://cdn.equalweb.com/core/accessibility.js", False),
        ("https://notfairphone.com/x", False),
    ],
)
def test_first_party_means_a_fairphone_address(url, expected):
    assert is_first_party(url, SHOP) is expected


def test_broken_page_fails():
    assert classify_page_status("https://www.fairphone.com/x", 404).verdict == FAIL
    assert classify_page_status("https://www.fairphone.com/x", None).verdict == FAIL
    assert classify_page_status("https://www.fairphone.com/x", 200) is None
    assert classify_page_status("https://www.fairphone.com/x", 301) is None


def test_shop_server_error_or_missing_script_fails():
    assert classify_resource_status("https://www.fairphone.com/a.js", 404, "script", SHOP).verdict == FAIL
    assert classify_resource_status("https://www.fairphone.com/x", 500, "fetch", SHOP).verdict == FAIL


def test_missing_shop_image_is_reported_not_failed():
    """Seen live: country flag images answered 404 on the address page."""
    finding = classify_resource_status("https://www.fairphone.com/de/base/static/img/flags/bq.png", 404, "image", SHOP)
    assert finding.verdict == REPORT
    assert finding.first_party


def test_third_party_errors_are_reported_not_failed():
    """Seen live: an analytics service answered 503."""
    finding = classify_resource_status("https://api.eu1.exponea.com/webxp/link-ids", 503, "fetch", SHOP)
    assert finding.verdict == REPORT
    assert not finding.first_party


YOTPO_STACK = """TypeError: Cannot read properties of null (reading 'appendChild')
    at value (https://cdn-widgetsrepository.yotpo.com/widget-assets/widget-loyalty-campaigns/app.v0.13.0-4610.js:13:173215)
    at <anonymous> (https://cdn-widgetsrepository.yotpo.com/widget-assets/app.js:33:168682)"""
SHOP_STACK = """TypeError: x is undefined
    at Object.start (https://www.fairphone.com/web/assets/3631162-d998b8d/2/web.assets_frontend_lazy.min.js:8394:12)"""


def test_script_owner_is_read_from_the_stack_trace():
    assert script_source(SHOP_STACK).startswith("https://www.fairphone.com/web/assets/")
    assert script_source(YOTPO_STACK).startswith("https://cdn-widgetsrepository.yotpo.com/")
    assert script_source("TypeError: no addresses here") is None


def test_shop_script_crash_fails():
    assert classify_script_error("TypeError: x is undefined", SHOP_STACK, SHOP).verdict == FAIL


def test_third_party_script_crash_is_reported():
    """Seen live on /fr/keep-club-fairphone: Yotpo's loyalty widget crashes on load."""
    finding = classify_script_error("Cannot read properties of null", YOTPO_STACK, SHOP)
    assert finding.verdict == REPORT
    assert "yotpo.com" in finding.url


def test_script_crash_without_a_stack_is_reported_not_failed():
    assert classify_script_error("Script error.", None, SHOP).verdict == REPORT


def test_console_errors_are_reported_only():
    assert classify_console_error("Uncaught thing", "https://www.fairphone.com/a.js", SHOP).verdict == REPORT
    assert (
        classify_console_error("Failed to load resource: 404", "https://www.fairphone.com/a.png", SHOP).verdict
        == REPORT
    )


def test_page_fails_when_any_finding_fails_or_bot_protection_answers():
    page = PageResult("https://www.fairphone.com/x", 200)
    assert not page.failed
    page.findings.append(classify_resource_status("https://www.googletagmanager.com/x", 500, "script", SHOP))
    assert not page.failed
    page.findings.append(classify_page_status(page.page, 404))
    assert page.failed
    assert PageResult("https://www.fairphone.com/y", 403, blocked=True).failed
