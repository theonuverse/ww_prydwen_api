from .._browser import _WWBrowser
from .character import Character

_CHARACTERS_BOX_SELECTOR = ".employees-container.ww-cards .pw-card.avatar-card .emp-name"

class Characters(_WWBrowser):
    def get(self, name: str) -> Character:
        url = f"https://www.prydwen.gg/wuthering-waves/characters/{name.lower()}"
        return Character(self._open(url))

    @property
    def all(self) -> dict[int, str]:
        url = "https://www.prydwen.gg/wuthering-waves/characters"
        return {
            i : char.inner_text() for i, char in enumerate(self._open(url).locator(_CHARACTERS_BOX_SELECTOR).all(), 1)
        }

