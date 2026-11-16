"""Cart page: read lines and totals, change quantity, remove a line, go to checkout."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from playwright.sync_api import Locator

from pages.base_page import BasePage
from utils.money import parse_price


@dataclass(frozen=True)
class CartUpdate:
    """What the shop's server answered to a cart change (POST /shop/cart/update_json)."""

    line_quantity: int
    cart_quantity: int
    cart_total: Decimal


class CartPage(BasePage):
    path = "/shop/cart"

    @property
    def heading(self) -> Locator:
        return self.page.get_by_role("heading", name=self.text("cart_heading"), level=1)

    def line(self, product_name: str) -> Locator:
        """One cart line: the block that holds the product's name and its quantity controls."""
        return (
            self.page.locator("main")
            .locator("div")
            .filter(has=self.page.get_by_role("heading", name=product_name, exact=True))
            .filter(has=self.page.get_by_role("link", name=self.text("cart_remove_line")))
            .last
        )

    def line_quantity(self, product_name: str) -> Locator:
        return self.line(product_name).get_by_role("textbox")

    def line_price(self, product_name: str) -> Decimal:
        """Unit price on the line, e.g. "€ 599.00" -> 599.00."""
        price = self.line(product_name).get_by_text(self.settings.region.currency_symbol).first
        return parse_price(price.inner_text())

    @property
    def summary(self) -> Locator:
        """The "Your order" box with subtotal, tax and total; holds the Go to checkout button."""
        return (
            self.page.locator("main div")
            .filter(has=self.page.get_by_role("button", name=self.text("cart_go_to_checkout")))
            .filter(has_text=self.settings.region.currency_symbol)
            .last
        )

    def total(self) -> Decimal:
        """Cart total: the last amount in the order summary ("Total: € 599.00")."""
        amounts = self.summary.get_by_text(self.settings.region.currency_symbol)
        return parse_price(amounts.last.inner_text())

    def _update(self, button: Locator) -> CartUpdate:
        """Click a quantity control and return the server's answer, so tests can compare screen and server.

        The answer is copied while it passes through the browser (route), because
        after some changes (e.g. removing the last line) the shop reloads the page
        and the browser forgets the answer. Only the page's own request is read;
        the test never calls the shop's API itself.
        """
        answers: list[dict] = []

        def keep_answer(route):
            response = route.fetch()
            answers.append(response.json())
            route.fulfill(response=response)

        self.page.route("**/shop/cart/update_json", keep_answer)
        try:
            with self.page.expect_response(lambda r: r.url.endswith("/shop/cart/update_json")):
                button.click()
        finally:
            self.page.unroute("**/shop/cart/update_json", keep_answer)
        result = answers[-1]["result"]
        # When the last line is removed the shop answers without line or amount fields: an empty cart.
        return CartUpdate(
            line_quantity=int(result.get("quantity", 0)),
            cart_quantity=int(result.get("cart_quantity", 0)),
            cart_total=Decimal(str(result.get("amount", 0))).quantize(Decimal("0.01")),
        )

    def add_one(self, product_name: str) -> CartUpdate:
        return self._update(self.line(product_name).get_by_role("link", name=self.text("cart_add_one")))

    def remove_line(self, product_name: str) -> CartUpdate:
        """Remove the whole line; the shop asks "Are you sure?" first."""
        self.line(product_name).get_by_role("link", name=self.text("cart_remove_line")).click()
        confirm = self.page.get_by_role("link", name=self.text("cart_remove_confirm"), exact=True)
        return self._update(confirm)

    @property
    def empty_message(self) -> Locator:
        return self.page.locator("main").get_by_text(self.text("cart_empty"), exact=True)

    def go_to_checkout(self) -> None:
        self.page.get_by_role("button", name=self.text("cart_go_to_checkout")).click()
