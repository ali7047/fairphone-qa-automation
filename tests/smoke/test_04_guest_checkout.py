"""Journey 4: start checkout without an account and stop at the address step."""

import re

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.product_page import ProductPage
from test_data.products import ProductChoice
from utils.evidence import attach_data, attach_screenshot, step


@allure.feature("Smoke journeys")
@allure.story("4. Guest checkout to the address step")
@pytest.mark.smoke
def test_guest_checkout_reaches_the_address_form(page: Page, settings: Settings, phone: ProductChoice):
    """
    Data:     phone from test_data/products.py. No personal data: nothing is typed.
    Steps:    1. Add the phone to the cart (as in journey 2).
              2. Click "Go to checkout", then "Checkout as guest".
              3. Stop. Do not type into the form, do not press "Next step".
    Expected: the address page (/shop/address) opens with the headings "Checkout" and
              "Address" and empty First name / Last name fields; the order summary still
              shows the phone.
    """
    attach_data("Test data: phone", phone)

    with step("1. Add the phone to the cart"):
        configurator = ProductPage(page, settings).open(phone.product_page).go_to_configurator()
        configurator.choose(phone)
        configurator.add_to_cart()

    with step("2. Go to checkout and choose guest checkout"):
        CartPage(page, settings).go_to_checkout()
        checkout = CheckoutPage(page, settings)
        expect(checkout.guest_checkout_link, "Expected a guest checkout option").to_be_visible()
        attach_screenshot(page, "Choice: guest or login")
        checkout.continue_as_guest()

    with step("3. Check the address step, then stop (nothing typed, nothing submitted)"):
        expect(page, "Expected the address step").to_have_url(re.compile(r"/shop/address"))
        expect(checkout.heading, f"Expected heading {checkout.text('checkout_heading')!r}").to_be_visible()
        expect(checkout.address_heading, f"Expected heading {checkout.text('address_heading')!r}").to_be_visible()
        for field in ("first_name", "last_name"):
            expect(checkout.field(field), f"Expected an empty {checkout.text(field)!r} field").to_have_value("")
        expect(page.locator("main"), f"Expected {phone.product_name!r} in the order summary").to_contain_text(
            phone.product_name
        )
        attach_screenshot(page, "Address step (journey ends here)")
    # Journey ends here on purpose: the live shop must never receive a checkout form.
