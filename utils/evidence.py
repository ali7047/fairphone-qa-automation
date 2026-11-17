"""Evidence for the test report (Allure): named steps and attachments.

Every journey records what it did and what it saw, so a reader can follow a
test in the report without opening the code:
- step(...)            a named step, shown as a block in the report
- attach_screenshot()  what the customer saw at that moment
- attach_data()        the data a check used (test data, prices, server answers)
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from typing import Any

import allure
from playwright.sync_api import Page


@contextmanager
def step(title: str) -> Iterator[None]:
    with allure.step(title):
        yield


def attach_screenshot(page: Page, name: str, full_page: bool = False) -> None:
    allure.attach(
        page.screenshot(full_page=full_page),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )


def attach_data(name: str, data: Any) -> None:
    """Attach structured data (dataclasses, dicts, Decimals) as readable JSON."""
    allure.attach(
        json.dumps(_plain(data), indent=2, ensure_ascii=False),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_check(name: str, expected: Any, actual: Any) -> None:
    """Attach one comparison as "expected vs actual", whether it passes or not."""
    attach_data(name, {"expected": expected, "actual": actual, "match": expected == actual})


def _plain(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _plain(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return value
