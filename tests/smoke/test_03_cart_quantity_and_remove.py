"""Journey 3: change the quantity, then remove the line; the cart ends empty."""

import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.cart_page import CartPage
from pages.product_page import ProductPage
from test_data.products import ProductChoice
from utils.evidence import attach_check, attach_data, attach_screenshot, step


@allure.feature("Smoke journeys")
@allure.story("3. Change quantity and remove")
@pytest.mark.smoke
def test_quantity_change_updates_totals_and_removing_the_line_empties_the_cart(
    page: Page, settings: Settings, phone: ProductChoice
):
    """
    Data:     phone from test_data/products.py; unit price read from the cart while the test runs.
    Steps:    1. Add the phone to the cart (as in journey 2).
              2. Click "Add one"; keep the shop's server answer (API) and read the screen (GUI).
              3. Click "Remove from cart" and confirm.
    Expected: after "Add one": quantity 2 and total = 2 x unit price, the same on screen
              (quantity field, header count, total) and in the server answer.
              After removing: the server reports 0 items; the screen shows the empty-cart
              message and the header cart icon shows 0.
    """
    attach_data("Test data: phone", phone)

    with step("1. Add the phone to the cart"):
        configurator = ProductPage(page, settings).open(phone.product_page).go_to_configurator()
        configurator.choose(phone)
        configurator.add_to_cart()
        cart = CartPage(page, settings)
        unit_price = cart.line_price(phone.product_name)
        expected_total = unit_price * 2
        attach_data("Unit price from the cart", {"unit_price": unit_price, "expected_total_for_2": expected_total})
        attach_screenshot(page, "Cart with 1 phone")

    with step("2. Click 'Add one' and compare server answer (API) with the screen (GUI)"):
        server = cart.add_one(phone.product_name)
        attach_data("Server answer (POST /shop/cart/update_json)", server)
        expect(cart.line_quantity(phone.product_name), "Expected quantity field 2").to_have_value("2")
        expect(cart.cart_link, "Expected header cart icon 2").to_have_text("2")
        screen_total = cart.total()
        attach_screenshot(page, "Cart with quantity 2")
        attach_check("Server line quantity", 2, server.line_quantity)
        attach_check("Server total vs 2 x unit price", expected_total, server.cart_total)
        attach_check("Screen total vs 2 x unit price", expected_total, screen_total)
        assert server.line_quantity == 2, f"Expected server line quantity 2, actual {server.line_quantity}"
        assert server.cart_total == expected_total, (
            f"Expected server cart total {expected_total} (2 x {unit_price}), actual {server.cart_total}"
        )
        assert screen_total == expected_total, (
            f"Expected cart total on screen {expected_total} (2 x {unit_price}), actual {screen_total}"
        )

    with step("3. Remove the line and confirm"):
        server = cart.remove_line(phone.product_name)
        attach_data("Server answer after removing", server)
        attach_check("Server item count after removing", 0, server.cart_quantity)
        assert server.cart_quantity == 0, (
            f"Expected server to report an empty cart, actual {server.cart_quantity} items"
        )
        expect(cart.empty_message, f"Expected the message {cart.text('cart_empty')!r}").to_be_visible()
        expect(cart.cart_link, "Expected header cart icon 0").to_have_text("0")
        attach_screenshot(page, "Empty cart")
