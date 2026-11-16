"""Journey 2: open a phone, choose a colour, add it to the cart; the cart matches the product page."""

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.cart_page import CartPage
from pages.product_page import ProductPage
from test_data.products import ProductChoice
from utils.evidence import attach_check, attach_data, attach_screenshot, step


@allure.feature("Smoke journeys")
@allure.story("2. Product page to cart")
@pytest.mark.smoke
def test_phone_with_chosen_colour_is_added_to_cart_at_configurator_price(
    page: Page, settings: Settings, phone: ProductChoice
):
    """
    Data:     phone, colour and names from test_data/products.py
              (EU English: The Fairphone (Gen. 6), Forest Green).
              The price is read from the configurator while the test runs.
    Steps:    1. Open the phone's product page and follow its buy link to the configurator.
              2. Choose the colour (US: also "set up connectivity later").
              3. Read the configurator price, click Add to cart (cart offers are skipped).
              4. Read the cart line, quantity, header count and total.
    Expected: the cart has one line with the product name and chosen colour, quantity 1;
              line price, cart total and configurator price are equal; header count is 1.
    """
    attach_data("Test data: phone", phone)

    with step("1. Open the product page and go to the configurator"):
        configurator = ProductPage(page, settings).open(phone.product_page).go_to_configurator()
        attach_screenshot(page, "Configurator")

    with step(f"2. Choose colour {phone.colour!r}"):
        configurator.choose(phone)
        attach_screenshot(page, "Configurator with chosen options")

    with step("3. Read the price and add to cart"):
        configurator_price = configurator.price()
        attach_data("Configurator price", {"price": configurator_price, "currency": settings.region.currency})
        configurator.add_to_cart()

    with step("4. Check the cart"):
        cart = CartPage(page, settings)
        line = cart.line(phone.product_name)
        expect(line, f"Expected a cart line for {phone.product_name!r}").to_be_visible()
        attach_screenshot(page, "Cart")
        expect(line, f"Expected the chosen colour {phone.colour!r} on the cart line").to_contain_text(phone.colour)
        expect(cart.line_quantity(phone.product_name), "Expected quantity 1").to_have_value("1")
        expect(cart.cart_link, "Expected the header cart icon to show 1 item").to_have_text("1")

        line_price = cart.line_price(phone.product_name)
        total = cart.total()
        attach_check("Cart line price vs configurator price", configurator_price, line_price)
        attach_check("Cart total vs configurator price x 1", configurator_price, total)
        assert line_price == configurator_price, (
            f"Expected cart line price {configurator_price} (configurator), actual {line_price}"
        )
        assert total == configurator_price, (
            f"Expected cart total {configurator_price} (configurator price x 1), actual {total}"
        )
