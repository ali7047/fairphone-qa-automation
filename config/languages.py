"""Visible texts per shop language.

Page objects find buttons and links by the text a customer sees. That text
changes with the language ("Colour" / "Kleur"), so page objects look it up here
instead of hard-coding English. Only texts checked on the live shop are listed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    code: str
    texts: dict[str, str]

    def text(self, key: str) -> str:
        """Visible text for `key`, e.g. text("colour_group") -> "Kleur" in Dutch."""
        if key not in self.texts:
            raise LookupError(
                f"No {self.code!r} text for {key!r} yet: check it on the live shop "
                f"and add it to config/languages.py"
            )
        return self.texts[key]


LANGUAGES: dict[str, Language] = {
    "en": Language(
        "en",
        {
            # Header menu
            "menu_shop": "Shop",
            "menu_about": "About",
            "menu_smartphones": "Smartphones",
            "menu_accessories": "Accessories",
            "menu_spare_parts": "Spare parts",
            # Configurator
            "model_group": "Model",
            "colour_group": "Colour",
            "colour_horizon_black": "Horizon Black",
            "colour_forest_green": "Forest Green",
            "product_gen6": "The Fairphone (Gen. 6)",
        },
    ),
    "nl": Language(
        "nl",
        {
            # Header menu
            "menu_shop": "Shop",
            "menu_about": "Over Ons",
            "menu_smartphones": "Smartphones",
            "menu_accessories": "Accessoires",
            "menu_spare_parts": "Onderdelen",
            # Configurator
            "model_group": "Model",
            "colour_group": "Kleur",
            "colour_horizon_black": "Horizon Zwart",
            "colour_forest_green": "Forest Groen",
            "product_gen6": "De Fairphone (Gen. 6)",
        },
    ),
}
