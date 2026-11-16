"""Known issue: the address step accepts "37" as street + house number without any warning."""

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.product_page import ProductPage
from test_data.products import ProductChoice
from utils.evidence import attach_check, attach_data, attach_screenshot, step

INCOMPLETE_STREET = "37"  # a house number without a street name


@allure.feature("Known issues")
@allure.story("Address validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.known_issue
def test_address_step_warns_when_street_name_is_missing(page: Page, settings: Settings, phone: ProductChoice):
    """
    Data:     phone from test_data/products.py; street + house number = "37" (no street name).
              Nothing else is typed; no personal data.
    Steps:    1. Add the phone to the cart; check iDEAL is among the payment methods.
              2. Go to checkout, continue as guest, reach the address form.
              3. Block every form submit, then type "37" into "Street address + house number"
                 and leave the field (Tab). Do not press Next.
    Expected: the shop warns that the street name is missing (field marked invalid or an
              error message), as it would for any delivery address without a street.
    Today:    FAILS - no warning; "37" is accepted. A customer can get to payment with an
              address that cannot be delivered (manual correction by customer service,
              Medium severity). See knowledge/site-observations.md.
    """
    attach_data("Test data", {"phone": phone, "street_and_house_number": INCOMPLETE_STREET})

    with step("1. Add the phone to the cart and check iDEAL is offered"):
        configurator = ProductPage(page, settings).open(phone.product_page).go_to_configurator()
        configurator.choose(phone)
        configurator.add_to_cart()
        cart = CartPage(page, settings)
        if settings.region.code == "eu":
            expect(page.locator("main").get_by_role("img", name="iDEAL"), "Expected iDEAL among the payment methods").to_be_visible()
        attach_screenshot(page, "Cart with payment methods")

    with step("2. Go to checkout as guest"):
        cart.go_to_checkout()
        checkout = CheckoutPage(page, settings)
        checkout.continue_as_guest()
        expect(page).to_have_url(re.compile(r"/shop/address"))

    with step(f"3. Type {INCOMPLETE_STREET!r} as street + house number (submits blocked)"):
        checkout.block_form_submits()
        checkout.type_into("street", INCOMPLETE_STREET)
        street = checkout.field("street")
        street.scroll_into_view_if_needed()
        attach_screenshot(page, f"Address form with street = {INCOMPLETE_STREET!r}")
        attach_data("Form posts blocked (must be empty: nothing was sent)", checkout.blocked_submits)
        assert checkout.blocked_submits == [], f"Expected no form post, actual {checkout.blocked_submits}"

        flagged = checkout.field_is_flagged("street")
        attach_check("Street field marked as wrong by the shop", True, flagged.count() > 0)
        expect(
            flagged,
            f"Expected the shop to flag {INCOMPLETE_STREET!r} (no street name), but it accepted it",
        ).to_be_visible(timeout=3_000)
