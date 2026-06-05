from playwright.sync_api import Page

_TAB_SELECTOR = ".tabs .single-tab"
_SKILL_CATEGORY_SELECTOR = ".tabs-skills .single-tab"
_SKILL_BOX_SELECTOR = ".tab-inside.active:has(.tabs-skills) .tab-inside.active"
_RESONANCE_CHAIN_SELECTOR = ".skills.dupes .box"
_UPGRADE_BOX_SELECTOR = ".upgrade-materials .box"


class Multipliers:
    """Stores and retrieves skill multiplier data across different levels."""

    def __init__(self, data: dict[int, str]) -> None:
        """
        Args:
            data: A dictionary mapping level integers to string values.
        """
        self._data = data

    def get(self, level: int) -> str:
        """Retrieves the multiplier value for a specific level."""
        return self._data[level]

    @property
    def all(self) -> dict[int, str]:
        """Returns all level mappings."""
        return self._data

    def __repr__(self) -> str:
        return f"Multipliers({self._data!r})"


class Skill:
    """Represents a character skill with its metadata and level-based values."""

    def __init__(
        self,
        category: str,
        name: str,
        description: str,
        multipliers: Multipliers
    ) -> None:
        """
        Args:
            category: The skill category (e.g., Active, Passive).
            name: The display name of the skill.
            description: The descriptive text of the skill.
            multipliers: A Multipliers instance containing level scaling data.
        """
        self.category = category
        self.name = name
        self.description = description
        self.multipliers = multipliers

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, category={self.category!r})"


class SkillAccessor:
    """Helper class that allows calling directly with a 1-based index."""

    def __init__(self, skills_instance: "Skills", category_index: int) -> None:
        self._skills = skills_instance
        self._category_index = category_index

    def __call__(self, index: int) -> Skill:
        """Retrieves the skill at the given index (1-based)."""
        return self._skills._fetch(self._category_index, index)

    def _get_total_count(self) -> int:
        """Helper to determine how many skills exist in this category on the page."""
        self._skills._page.locator(_SKILL_CATEGORY_SELECTOR).nth(self._category_index).click()
        return self._skills._page.locator(_SKILL_BOX_SELECTOR).locator(".box.skill-new").count()

    @property
    def all(self) -> dict[int, Skill]:
        """Retrieves all available skills in this category as a 1-based dictionary."""
        count = self._get_total_count()
        return {i: self(i) for i in range(1, count + 1)}


class ActiveSkills(SkillAccessor):
    """Accessor for active skills with explicit properties."""

    def __init__(self, skills_instance: "Skills") -> None:
        super().__init__(skills_instance, category_index=0)

    @property
    def basic_attack(self) -> Skill:
        """Retrieves the Basic Attack (Index 1)."""
        return self(1)

    @property
    def resonance_skill(self) -> Skill:
        """Retrieves the Resonance Skill (Index 2)."""
        return self(2)

    @property
    def resonance_liberation(self) -> Skill:
        """Retrieves the Resonance Liberation (Index 3)."""
        return self(3)


class PassiveSkills(SkillAccessor):
    """Accessor for passive skills with dynamic index mapping based on skill count."""

    def __init__(self, skills_instance: "Skills") -> None:
        super().__init__(skills_instance, category_index=1)

    def _get_total_passive_count(self) -> int:
        """Helper to determine how many passive skills this character has on the page."""
        self._skills._page.locator(_SKILL_CATEGORY_SELECTOR).nth(self._category_index).click()
        return self._skills._page.locator(_SKILL_BOX_SELECTOR).locator(".box.skill-new").count()

    @property
    def forte_circuit(self) -> Skill:
        """Retrieves the main Forte Circuit (Always Index 1)."""
        return self(1)

    @property
    def forte_circuit_tune(self) -> Skill | None:
        """Retrieves the Forte Circuit Tune if it exists, otherwise returns None."""
        if self._get_total_passive_count() == 4:
            return self(2)
        return None

    @property
    def inherent_skill_1(self) -> Skill:
        """Retrieves the first Inherent Skill (Index 2 if 3 skills total, Index 3 if 4 skills total)."""
        index = 3 if self._get_total_passive_count() == 4 else 2
        return self(index)

    @property
    def inherent_skill_2(self) -> Skill:
        """Retrieves the second Inherent Skill (Index 4 if 3 skills total, Index 4 if 4 skills total)."""
        index = 4 if self._get_total_passive_count() == 4 else 3
        return self(index)


class ConcertoSkills(SkillAccessor):
    """Accessor for concerto skills with explicit properties."""

    def __init__(self, skills_instance: "Skills") -> None:
        super().__init__(skills_instance, category_index=2)

    @property
    def intro_skill(self) -> Skill:
        """Retrieves the Intro Skill (Index 1)"""
        return self(1)

    @property
    def outro_skill(self) -> Skill:
        """Retrieves the Outro Skill (Index 2)"""
        return self(2)


class Skills:
    """Interface to interact with and scrape character skill data."""

    def __init__(self, page: Page) -> None:
        self._page = page

        # Instanzen mit echten Properties für IntelliSense Support
        self.active = ActiveSkills(self)
        self.passive = PassiveSkills(self)
        self.concerto = ConcertoSkills(self)

    def _fetch(self, skill_category_index: int, skill_box_index: int) -> Skill:
        """Internal helper to navigate and scrape skill data from the UI."""
        self._page.locator(_SKILL_CATEGORY_SELECTOR).nth(skill_category_index).click()

        category = self._page.locator(_SKILL_CATEGORY_SELECTOR).nth(skill_category_index).inner_text()
        skill = self._page.locator(_SKILL_BOX_SELECTOR).locator(".box.skill-new").nth(skill_box_index - 1)

        name = skill.locator(".skill-info").inner_text()
        description = skill.locator(".skill-with-coloring").inner_text()

        data = {}
        button = skill.locator("button")

        # Wenn der Button da ist (nur bei Forte Circuit), durchklicken.
        # Bei Tune und Inherent-Skills wird dieser Block einfach übersprungen.
        if button.count() > 0:
            button.click()
            slider = skill.locator("[role='slider']")
            slider.click()

            for i in range(1, 11):
                if i > 1:
                    slider.press("ArrowRight")
                data[i] = skill.locator(".pw-accordion-body").inner_text()

        return Skill(category, name, description, Multipliers(data))


class ResonanceChainNode:
    """Represents a single node in a character's resonance chain."""

    def __init__(self, sequence: str, name: str, description: str) -> None:
        """
        Args:
            sequence: The sequence identifier for the node.
            name: The name of the resonance effect.
            description: Details of the resonance effect.
        """
        self.sequence = sequence
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"ResonanceChainNode(sequence={self.sequence!r}, name={self.name!r})"


class Material:
    """Represents an upgrade material requirement."""

    def __init__(self, name: str | None, quantity: str | None) -> None:
        """
        Args:
            name: The name of the material.
            quantity: The required amount of the material.
        """
        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"Material(name={self.name!r}, quantity={self.quantity!r})"


class ResonanceChain:
    """Interface to interact with and scrape character resonance chain nodes."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def _parse_node(self, node) -> ResonanceChainNode:
        """Parse helper function."""
        sequence = node.locator(".skill-icon").inner_text()
        name = node.locator(".skill-info").inner_text()
        description = node.locator(".skill-with-coloring").inner_text()

        return ResonanceChainNode(sequence, name, description)

    def get(self, index: int) -> ResonanceChainNode:
        """Retrieves a specific resonance node by index (1-based)."""
        node = self._page.locator(_RESONANCE_CHAIN_SELECTOR).nth(index - 1)
        return self._parse_node(node)

    @property
    def all(self) -> dict[int, ResonanceChainNode]:
        """Retrieves all resonance nodes in the chain."""
        return {i: self._parse_node(node) for i, node in enumerate(self._page.locator(_RESONANCE_CHAIN_SELECTOR).all(), 1)}


class UpgradeCategory:
    """Represents a specific category of upgrade materials (e.g., Ascension)."""

    def __init__(self, page: Page, box_index: int) -> None:
        self._page = page
        self._box_index = box_index

    def name(self) -> str | None:
        """Returns the name of the upgrade category."""
        if self._page.locator(_UPGRADE_BOX_SELECTOR).count() == 0:
            return None
        box = self._page.locator(_UPGRADE_BOX_SELECTOR).nth(self._box_index)
        return box.locator("h5").inner_text()

    def _parse_material(self, material) -> Material:
        """Parse helper function."""
        name = material.locator("strong[class*='rarity-']").inner_text()
        quantity = material.locator("strong").nth(0).inner_text()
        return Material(name, quantity)

    def get(self, index: int) -> Material:
        """Retrieves a specific material by index."""
        if self._page.locator(_UPGRADE_BOX_SELECTOR).count() == 0:
            return Material(None, None)

        box = self._page.locator(_UPGRADE_BOX_SELECTOR).nth(self._box_index)
        material = box.locator("li").nth(index - 1)
        return self._parse_material(material)

    @property
    def all(self) -> dict[int, Material]:
        """Retrieves all materials required for this category."""
        if self._page.locator(_UPGRADE_BOX_SELECTOR).count() == 0:
            return {}
        box = self._page.locator(_UPGRADE_BOX_SELECTOR).nth(self._box_index)
        return {i: self._parse_material(mat) for i, mat in enumerate(box.locator("li").all(), 1)}


class UpgradeMaterials:
    """Interface to access various character upgrade material categories."""

    def __init__(self, page: Page) -> None:
        self._page = page

    @property
    def character_ascension(self) -> UpgradeCategory:
        """Returns the ascension material category."""
        return UpgradeCategory(self._page, 0)

    @property
    def skill_upgrades(self) -> UpgradeCategory:
        """Returns the skill upgrade material category."""
        return UpgradeCategory(self._page, 1)


class Kit:
    """Primary entry point for interacting with a character's kit page."""

    def __init__(self, page: Page) -> None:
        self._page = page
        self._page.locator(_TAB_SELECTOR).nth(0).click()

    @property
    def skills(self) -> Skills:
        """Returns the interface for interacting with character skills."""
        return Skills(self._page)

    @property
    def resonance_chain(self) -> ResonanceChain:
        """Returns the interface for interacting with the resonance chain."""
        return ResonanceChain(self._page)

    @property
    def upgrade_materials(self) -> UpgradeMaterials:
        """Returns the interface for interacting with upgrade materials."""
        return UpgradeMaterials(self._page)
