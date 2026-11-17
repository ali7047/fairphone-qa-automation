"""Visible texts per shop language.

Page objects find buttons and links by the text a customer sees. That text
changes with the language ("Remove from cart" / "Verwijderen uit winkelwagen"),
so page objects look it up here. Only texts checked on the live shop are listed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str
    texts: dict[str, str]

    def text(self, key: str) -> str:
        """Visible text for `key`, e.g. text("cart_heading") -> "Winkelwagen" in Dutch."""
        if key not in self.texts:
            raise LookupError(
                f"No {self.code!r} text for {key!r} yet: check it on the live shop and add it to config/languages.py"
            )
        return self.texts[key]


LANGUAGES: dict[str, Language] = {
    "en": Language(
        "en",
        {
            # Header
            "menu_about": "About",
            # Product page and configurator
            "buy_now": "BUY NOW",
            "add_to_cart": "Add to cart",
            # Pop-ups in the cart
            "offer_skip": "continue without adding",
            "offer_go_to_cart": "GO TO CART",
            # Cart
            "cart_heading": "Cart",
            "cart_add_one": "Add one",
            "cart_remove_one": "Remove one",
            "cart_remove_line": "Remove from cart",
            "cart_remove_confirm": "remove product",
            "cart_empty": "Your cart is empty",
            "cart_go_to_checkout": "Go to checkout",
            # Checkout
            "checkout_as_guest": "Checkout as guest",
            "checkout_heading": "Checkout",
            "address_heading": "Address",
            "first_name": "First name",
            "last_name": "Last name",
            "street": "Street address + house number",
        },
    ),
    "nl": Language(
        "nl",
        {
            # Header
            "menu_about": "Over Ons",
            # Product page and configurator
            "buy_now": "KOOP NU",
            "add_to_cart": "In winkelwagen",
            # Pop-ups in the cart
            "offer_skip": "Verdergaan zonder toevoegen",
            "offer_go_to_cart": "GA NAAR WINKELWAGEN",
            # Cart
            "cart_heading": "Winkelwagen",
            "cart_add_one": "Eén toevoegen",
            "cart_remove_one": "Eén verwijderen",
            "cart_remove_line": "Verwijderen uit winkelwagen",
            "cart_remove_confirm": "product verwijderen",
            "cart_empty": "Je winkelwagen is leeg",
            "cart_go_to_checkout": "Naar afrekenen",
            # Checkout
            "checkout_as_guest": "Uitchecken als gast",
            "checkout_heading": "Kassa",
            "address_heading": "Adres",
            "first_name": "Voornaam",
            "last_name": "Achternaam",
            "street": "Adres + huisnummer",
        },
    ),
}
