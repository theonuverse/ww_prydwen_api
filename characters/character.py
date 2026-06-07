from playwright.sync_api import Page
from .kit import Kit
from .review import Review
from .build import Build


class Character:
    def __init__(self, page: Page) -> None:
        self._page = page

    @property
    def name(self) -> str:
        """
        Retrieves the character name.
        """
        return self._page.locator(".character-top .left-info strong").inner_text()

    @property
    def introduction(self) -> str:
        """
        Retrieves the character introduction.
        """
        raw_introduction = self._page.locator(".character-intro .combined").inner_text()
        _, _, content = raw_introduction.partition(". ")
        introduction = " ".join(content.split())
        return introduction

    @property
    def kit(self) -> Kit:
        """
        Retrieves the character kit.
        """
        return Kit(self._page)

    @property
    def review(self) -> Review:
        """
        Retrieves the character review.
        """
        return Review(self._page)

    @property
    def build(self) -> Build:
        """Retrieves the character build."""
        return Build(self._page)
