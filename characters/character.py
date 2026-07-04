"""Top-level Character interface aggregating role, kit, review, and build data."""
from playwright.sync_api import Page

from ._common import IndexedCollection, safe_inner_text
from .build import Build
from .kit import Kit
from .review import Review

_ROLE_SELECTOR = ".role"


class CharacterRoles(IndexedCollection[str]):
    """A character's role(s), using the site's dual-count DOM approach.

    NOTE: this preserves the exact original scaling rule verbatim:
    a DOM count of 2 means 1 logical role; any other DOM count
    (typically 4) means 2 logical roles. This is a direct port, not a
    generalization — it intentionally does not attempt to handle DOM
    counts of 0/1/3/5+ any differently than the original did.
    """

    _item_label = "Role"

    def __init__(self, page: Page) -> None:
        self._page = page

    def _count(self) -> int:
        dom_count = self._page.locator(_ROLE_SELECTOR).count()
        return 1 if dom_count == 2 else 2

    def _fetch(self, index: int) -> str:
        return safe_inner_text(self._page.locator(_ROLE_SELECTOR), index=index - 1)


class Character:
    """Entry point for a single character's page: name, intro, role, kit, review, build."""

    def __init__(self, page: Page) -> None:
        self._page = page

    @property
    def name(self) -> str:
        """The character's display name."""
        return safe_inner_text(self._page.locator(".character-top .left-info strong"))

    @property
    def introduction(self) -> str:
        """The character's introduction blurb, with the leading sentence fragment removed."""
        raw_introduction = self._page.locator(".character-intro .combined").inner_text()
        _, _, content = raw_introduction.partition(". ")
        return " ".join(content.split())

    @property
    def role(self) -> CharacterRoles:
        """The character's role(s)."""
        return CharacterRoles(self._page)

    @property
    def kit(self) -> Kit:
        """The character's kit (skills, resonance chain, upgrade materials)."""
        return Kit(self._page)

    @property
    def review(self) -> Review:
        """The character's review (pros/cons, tier ratings, write-up)."""
        return Review(self._page)

    @property
    def build(self) -> Build:
        """The character's recommended build (weapons, echoes, stats, skill priority)."""
        return Build(self._page)
