"""Unit tests for test_data/products.py (no browser, no network).

Why: every journey picks its phone from this table. A missing shop/language
pair would only show up as a confusing browser failure.
"""

import pytest

from config.settings import REGIONS
from test_data.products import MENU_TARGETS, PHONES, phone_for


def test_every_shop_and_language_has_a_test_phone_and_menu_target():
    for region in REGIONS.values():
        for language in region.languages:
            assert (region.code, language) in PHONES, f"No test phone for {region.code}/{language}"
            assert (region.code, language) in MENU_TARGETS, f"No menu target for {region.code}/{language}"


def test_extra_choice_comes_with_its_group():
    for key, phone in PHONES.items():
        assert bool(phone.extra_choice_group) == bool(phone.extra_choice), f"{key}: group and choice go together"


def test_unknown_shop_language_fails_clearly():
    with pytest.raises(LookupError, match="No test phone for shop 'us' in 'nl'"):
        phone_for("us", "nl")
