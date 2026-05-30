from playwright.sync_api import Page
from ._browser import _WWBrowser

_TAB_SELECTOR = ".tabs .single-tab"
_SKILL_CATEGORY_SELECTOR = ".tabs-skills .single-tab"
_SKILL_BOX_SELECTOR = ".tab-inside.active:has(.tabs-skills) .tab-inside.active"
_RESONANCE_CHAIN_SELECTOR = ".skills.dupes .box"


class Multipliers:
    def __init__(self, data: dict[int, str]) -> None:
        self._data = data

    def get(self, level: int) -> str:
        return self._data[level]

    def all(self) -> dict[int, str]:
        return self._data

    def __repr__(self) -> str:
        return f"Multipliers({self._data!r})"


class Skill:
    def __init__(
        self,
        category: str,
        name: str,
        type: str,
        description: str,
        multipliers: Multipliers
    ) -> None:
        self.category = category
        self.name = name
        self.type = type
        self.description = description
        self.multipliers = multipliers

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, category={self.category!r})"


class Skills:
    def __init__(self, page: Page) -> None:
        self._page = page

    def _fetch(self, skill_category_index: int, skill_box_index: int) -> Skill:
        self._page.locator(_SKILL_CATEGORY_SELECTOR).nth(skill_category_index).click()
        category = self._page.locator(_SKILL_CATEGORY_SELECTOR).nth(skill_category_index).inner_text()
        skill = self._page.locator(_SKILL_BOX_SELECTOR).locator(".box.skill-new").nth(skill_box_index - 1)
        name = skill.locator(".skill-info").inner_text()
        type_ = skill.locator(".skill-icon").inner_text()
        description = skill.locator(".skill-with-coloring").inner_text()
        skill.locator("button").click()
        slider = skill.locator("[role='slider']")
        slider.click()
        data: dict[int, str] = {}
        for i in range(1, 11):
            if i > 1:
                slider.press("ArrowRight")
            data[i] = skill.locator(".pw-accordion-body").inner_text()
        return Skill(category, name, type_, description, Multipliers(data))

    def active(self, index: int) -> Skill:
        return self._fetch(0, index)

    def passive(self, index: int) -> Skill:
        return self._fetch(1, index)

    def concerto(self, index: int) -> Skill:
        return self._fetch(2, index)


class ResonanceChainNode:
    def __init__(self, sequence: str, name: str, description: str) -> None:
        self.sequence = sequence
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"ResonanceChainNode(sequence={self.sequence!r}, name={self.name!r})"


class ResonanceChain:
    def __init__(self, page: Page) -> None:
        self._page = page

    def _fetch(self, index: int) -> ResonanceChainNode:
        node = self._page.locator(_RESONANCE_CHAIN_SELECTOR).nth(index - 1)
        sequence = node.locator(".skill-icon").inner_text()
        name = node.locator(".skill-info").inner_text()
        description = node.locator(".skill-with-coloring").inner_text()
        return ResonanceChainNode(sequence, name, description)

    def get(self, index: int) -> ResonanceChainNode:
        return self._fetch(index)

    def all(self) -> dict[int, ResonanceChainNode]:
        return {i: self._fetch(i) for i in range(1, 7)}


class Kit:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.locator(_TAB_SELECTOR).nth(0).click()

    def skills(self) -> Skills:
        return Skills(self._page)

    def resonance_chain(self) -> ResonanceChain:
        return ResonanceChain(self._page)


class Character:
    def __init__(self, page: Page) -> None:
        self._page = page

    def kit(self) -> Kit:
        return Kit(self._page)


class Characters(_WWBrowser):
    def get(self, url: str) -> Character:
        return Character(self._open(url))
