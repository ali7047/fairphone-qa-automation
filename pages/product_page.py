"""Product page and configurator: choose a phone and a colour, add it to the cart."""

from __future__ import annotations

from decimal import Decimal

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage
from pages.popups import CartOffers
from test_data.products import ProductChoice
from utils.money import parse_price


class ProductPage(BasePage):
    """Marketing page of one phone, e.g. /the-fairphone-gen-6."""

    @property
    def buy_link(self) -> Locator:
        """The link to the configurator (EU "BUY NOW" / "KOOP NU", US "configure your phone").

        Found by where it leads, because the label differs per shop. The EU page
        has extra copies in a sticky bar (section aria-label="Page sections", same
        in every language) that only slides in after scrolling; those are left out.
        """
        return self.page.locator("main section:not([aria-label='Page sections']) a[href*='/configure/']").first

    def go_to_configurator(self) -> ConfiguratorPage:
        self.buy_link.click()
        self.page.wait_for_url("**/configure/**")
        return ConfiguratorPage(self.page, self.settings)


class ConfiguratorPage(BasePage):
    """Choose model options and colour, then Add to cart."""

    @property
    def add_to_cart_area(self) -> Locator:
        """The bar at the bottom with the price and the Add to cart button.

        It is a region named like its button ("Add to cart" / "In winkelwagen").
        """
        return self.page.get_by_role("region", name=self.text("add_to_cart"))

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.get_by_role("button", name=self.text("add_to_cart"))

    def option(self, group: str, name: str) -> Locator:
        return self.page.get_by_role("radiogroup", name=group).get_by_role("radio", name=name)

    def price(self) -> Decimal:
        """Price shown next to Add to cart, read from the page now (e.g. "€ 599" -> 599.00)."""
        price_text = self.add_to_cart_area.get_by_text(self.settings.region.currency_symbol).first
        expect(price_text).to_be_visible()
        return parse_price(price_text.inner_text())

    def choose(self, choice: ProductChoice) -> None:
        """Pick the colour (and the US connectivity option), waiting until the shop has switched product.

        After a colour click the page asks the server which product matches
        and only then switches the product it will add. Adding to cart before
        that answer adds the previous colour; see knowledge/site-observations.md.

        `expect(...).to_be_checked()` checks the result instead of assuming the
        click landed. Seen in CI: a pop-up ("Visiting from the US?") appeared at
        the moment of the click; the handler closed it, but that click was lost.
        So if the colour is not selected after the shop answered, click once more.
        """
        colour = self.option(choice.colour_group, choice.colour)
        self._select(colour, wait_for_shop=True)
        if choice.extra_choice_group:
            self._select(self.option(choice.extra_choice_group, choice.extra_choice))

    def _select(self, option: Locator, wait_for_shop: bool = False, attempts: int = 2) -> None:
        for attempt in range(1, attempts + 1):
            if wait_for_shop:
                with self.page.expect_response(lambda r: "/configure/" in r.url and r.request.method == "POST"):
                    option.click()
            else:
                option.click()
            try:
                expect(option).to_be_checked(timeout=3_000)
                return
            except AssertionError:
                if attempt == attempts:
                    raise

    def add_to_cart(self) -> None:
        """Add to cart, then skip the offers the cart shows for a new phone."""
        expect(self.add_to_cart_button).to_be_enabled()
        self.add_to_cart_button.click()
        self.page.wait_for_url("**/shop/cart")
        CartOffers(self.page, self.settings).skip_all()
