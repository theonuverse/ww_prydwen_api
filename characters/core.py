"""Top-level entry point for browsing prydwen.gg's Wuthering Waves character list."""
from .._browser import _WWBrowser
from .character import Character

_CHARACTERS_BOX_SELECTOR = ".employees-container.ww-cards .pw-card.avatar-card .emp-name"


class Characters(_WWBrowser):
    """Browse the Wuthering Waves character roster on prydwen.gg."""

    def get(self, name: str) -> Character:
        """Open a specific character's page by name (case-insensitive)."""
        url = f"https://www.prydwen.gg/wuthering-waves/characters/{name.lower()}"
        return Character(self._open(url))

    @property
    def all(self) -> dict[int, str]:
        """All character names currently listed on the roster page, 1-based."""
        url = "https://www.prydwen.gg/wuthering-waves/characters"
        return {
            i: char.inner_text() for i, char in enumerate(self._open(url).locator(_CHARACTERS_BOX_SELECTOR).all(), 1)
        }
