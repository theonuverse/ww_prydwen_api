from .._browser import _WWBrowser
from .character import Character


class Characters(_WWBrowser):
    def get(self, name: str) -> Character:
        url = f"https://www.prydwen.gg/wuthering-waves/characters/{name.lower()}"
        return Character(self._open(url))
