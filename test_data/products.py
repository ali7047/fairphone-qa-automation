"""Test data: the product each journey buys, per shop and language.

Kept out of the tests so that a new phone, colour or language means editing one
table, not every test. Prices are never listed here: tests read them from the
shop while they run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductChoice:
    """What a customer picks: which phone page, which colour, and the names they see."""

    product_page: str
    """Path of the product page the journey starts from."""
    product_name: str
    """Product name as shown in the cart, e.g. "The Fairphone (Gen. 6)"."""
    colour_group: str
    """Name of the colour choice on the configurator ("Colour", "Kleur", "Color")."""
    colour: str
    """Colour to pick. Must be in stock and differ from the default, so the test proves the choice is kept."""
    extra_choice_group: str | None = None
    """A further choice that must be made before Add to cart is enabled (US: connectivity)."""
    extra_choice: str | None = None
    """What to pick in that group: the option that commits the customer to nothing."""


PHONES: dict[tuple[str, str], ProductChoice] = {
    ("eu", "en"): ProductChoice(
        product_page="/the-fairphone-gen-6",
        product_name="The Fairphone (Gen. 6)",
        colour_group="Colour",
        colour="Forest Green",
    ),
    ("eu", "nl"): ProductChoice(
        product_page="/the-fairphone-gen-6",
        product_name="De Fairphone (Gen. 6)",
        colour_group="Kleur",
        colour="Forest Groen",
    ),
    ("us", "en"): ProductChoice(
        product_page="/the-fairphone-gen-6-plus",
        product_name="The Fairphone (Gen. 6+)",
        colour_group="Color",
        colour="Forest Green",
        extra_choice_group="Connectivity setup",
        extra_choice="I’ll set this up later",
    ),
}


def phone_for(region: str, language: str) -> ProductChoice:
    return _lookup(PHONES, region, language, "test phone")


@dataclass(frozen=True)
class MenuTarget:
    """A link in the header's Shop menu, and the page it must open."""

    link: str
    path: str
    heading: str


MENU_TARGETS: dict[tuple[str, str], MenuTarget] = {
    # The EU menu has a "Smartphones" group; the US menu lists the phone directly.
    ("eu", "en"): MenuTarget(link="Smartphones", path="/smartphones", heading="Smartphones"),
    ("eu", "nl"): MenuTarget(link="Smartphones", path="/nl/smartphones", heading="Smartphones"),
    ("us", "en"): MenuTarget(
        link="The Fairphone (Gen. 6+)", path="/the-fairphone-gen-6-plus", heading="The Fairphone (Gen. 6+)"
    ),
}


def menu_target_for(region: str, language: str) -> MenuTarget:
    return _lookup(MENU_TARGETS, region, language, "menu target")


def _lookup(table: dict, region: str, language: str, what: str):
    """Find the entry for a shop and language, or say exactly what is missing and where to add it."""
    try:
        return table[(region, language)]
    except KeyError:
        raise LookupError(f"No {what} for shop {region!r} in {language!r}: add one to test_data/products.py") from None
