from .._browser import _WWBrowser
from .character import Character


class Characters(_WWBrowser):
    def get(self, url: str) -> Character:
        if not url.startswith(("http://", "https://")):
            url = f"https://www.prydwen.gg/wuthering-waves/characters/{url.lower()}"
        return Character(self._open(url))
