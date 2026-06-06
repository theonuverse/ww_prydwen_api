from playwright.sync_api import Page

# Navigation (top level: KIT, REVIEW, BUILD, ...)
_MAIN_TAB_SELECTOR = ".tabs .single-tab"

# Skill category tabs (ACTIVE SKILLS, PASSIVE SKILLS, CONCERTO SKILLS)
_SKILL_CATEGORY_TAB_SELECTOR = ".tabs-skills .single-tab"

# The active skill panel (contains the skill boxes)
_SKILL_PANEL_SELECTOR = ".tab-inside.active:has(.tabs-skills) .tab-inside.active"

# Individual skill boxes inside the panel
_SKILL_BOX_CSS = ".box.skill-new"
_SKILL_NAME_CSS = ".skill-info"
_SKILL_DESC_CSS = ".skill-with-coloring"
_SKILL_MULTIPLIER_CSS = ".pw-accordion-body"

# Resonance chain section
_RESONANCE_CHAIN_SELECTOR = ".skills.dupes .box"

# Individual resonance chain information inside the panel
_RS_SEQUENCE_CS = ".skill-icon"
_RS_NAME_CS = ".skill-info"
_RS_DESCRIPTION_CS = ".skill-with-coloring"

# Upgrade materials section
_UPGRADE_BOX_SELECTOR = ".upgrade-materials .box"


class Multipliers:
    """Stores and retrieves skill multiplier data indexed by level."""

    def __init__(self, data: dict[int, str]) -> None:
        """Initialize Multipliers with level-indexed data."""
        self._data = data

    def get(self, level: int) -> str:
        """Retrieve the multiplier value for a specific level."""
        return self._data[level]

    @property
    def all(self) -> dict[int, str]:
        """Return all level-to-multiplier mappings."""
        return self._data

    def __repr__(self) -> str:
        return f"Multipliers({self._data!r})"


class Skill:
    """Represents a character skill with metadata and level-based scaling data."""

    def __init__(
        self,
        category: str,
        name: str,
        description: str,
        multipliers: Multipliers
    ) -> None:
        """Initialize a Skill instance."""
        self.category = category
        self.name = name
        self.description = description
        self.multipliers = multipliers

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, category={self.category!r})"


class ActiveSkills:
    """Accessor for active character skills with named properties."""

    def __init__(self, skills: "Skills") -> None:
        """Initialize ActiveSkills accessor."""
        self._skills = skills

    @property
    def basic_attack(self) -> Skill:
        """Retrieve the Basic Attack skill (Index 1)."""
        return self._skills._fetch(0, 1)

    @property
    def resonance_skill(self) -> Skill:
        """Retrieve the Resonance Skill (Index 2)."""
        return self._skills._fetch(0, 2)

    @property
    def resonance_liberation(self) -> Skill:
        """Retrieve the Resonance Liberation ultimate (Index 3)."""
        return self._skills._fetch(0, 3)


class PassiveSkills:
    """Accessor for passive character skills with dynamic properties."""

    def __init__(self, skills: "Skills") -> None:
        """Initialize PassiveSkills accessor."""
        self._skills = skills

    def _count(self) -> int:
        """Get total count of passive skills for this character."""
        self._skills._page.locator(_SKILL_CATEGORY_TAB_SELECTOR).nth(1).click()
        return self._skills._page.locator(_SKILL_CATEGORY_TAB_SELECTOR).locator(_SKILL_BOX_CSS).count()

    @property
    def forte_circuit(self) -> Skill:
        """Retrieve the Forte Circuit passive (Index 1)."""
        return self._skills._fetch(1, 1)

    @property
    def forte_circuit_tune(self) -> Skill | None:
        """Retrieve the Forte Circuit Tune if available, else None."""
        if self._count() == 4:
            return self._skills._fetch(1, 2)
        return None

    @property
    def inherent_skill_1(self) -> Skill:
        """Retrieve the first Inherent Skill (dynamic index based on Tune presence)."""
        return self._skills._fetch(1, 3 if self._count() == 4 else 2)

    @property
    def inherent_skill_2(self) -> Skill:
        """Retrieve the second Inherent Skill (always Index 3 or 4)."""
        return self._skills._fetch(1, 4 if self._count() == 4 else 3)


class ConcertoSkills:
    """Accessor for concerto-related entry and exit skills."""

    def __init__(self, skills: "Skills") -> None:
        """Initialize ConcertoSkills accessor."""
        self._skills = skills

    @property
    def intro_skill(self) -> Skill:
        """Retrieve the Intro Skill (Index 1)."""
        return self._skills._fetch(2, 1)

    @property
    def outro_skill(self) -> Skill:
        """Retrieve the Outro Skill (Index 2)."""
        return self._skills._fetch(2, 2)


class Skills:
    """Primary interface for accessing all character skill categories."""

    active: ActiveSkills
    passive: PassiveSkills
    concerto: ConcertoSkills

    def __init__(self, page: Page) -> None:
        """Initialize Skills interface with page and skill accessors."""
        self._page = page
        self.active = ActiveSkills(self)
        self.passive = PassiveSkills(self)
        self.concerto = ConcertoSkills(self)

    def _fetch(self, category_index: int, box_index: int) -> Skill:
        """Internal helper to navigate and scrape skill data from the page UI."""
        self._page.locator(_SKILL_CATEGORY_TAB_SELECTOR).nth(category_index).click()

        category = (
            self._page.locator(_SKILL_CATEGORY_TAB_SELECTOR).nth(category_index).inner_text()
        )

        skill = (
            self._page.locator(_SKILL_PANEL_SELECTOR).locator(_SKILL_BOX_CSS).nth(box_index - 1)
        )
        name = skill.locator(_SKILL_NAME_CSS).inner_text()
        description = skill.locator(_SKILL_DESC_CSS).inner_text()

        multiplier_values = {}

        button = skill.locator("button")
        if button.count() > 0:
            button.click()
            slider = skill.locator("[role='slider']")
            slider.click()
            for i in range(1, 11):
                if i > 1:
                    slider.press("ArrowRight")
                multiplier_values[i] = skill.locator(_SKILL_MULTIPLIER_CSS).inner_text()

        return Skill(category, name, description, Multipliers(multiplier_values))


class ResonanceChainNode:
    """Represents a single node in a character's resonance chain."""

    def __init__(self, sequence: str, name: str, description: str) -> None:
        """Initialize a ResonanceChainNode."""
        self.sequence = sequence
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"ResonanceChainNode(sequence={self.sequence!r}, name={self.name!r})"


class ResonanceChain:
    """Interface for accessing character resonance chain (constellation) nodes."""

    def __init__(self, page: Page) -> None:
        """Initialize ResonanceChain interface."""
        self._page = page

    def _parse_node(self, node) -> ResonanceChainNode:
        """Parse a DOM node element into a ResonanceChainNode instance."""
        sequence = node.locator(_RS_SEQUENCE_CS).inner_text()
        name = node.locator(_RS_NAME_CS).inner_text()
        description = node.locator(_RS_DESCRIPTION_CS).inner_text()

        return ResonanceChainNode(sequence, name, description)

    def get(self, index: int) -> ResonanceChainNode:
        """Retrieve a resonance chain node by 1-based index."""
        node = self._page.locator(_RESONANCE_CHAIN_SELECTOR).nth(index - 1)
        return self._parse_node(node)

    @property
    def all(self) -> dict[int, ResonanceChainNode]:
        """Retrieve all resonance chain nodes as a 1-based dictionary."""
        return {
            i: self._parse_node(node) for i, node in enumerate(self._page.locator(_RESONANCE_CHAIN_SELECTOR).all(), 1)
        }


class Material:
    """Represents a single upgrade material requirement."""

    def __init__(self, name: str | None, quantity: str | None) -> None:
        """Initialize a Material instance."""
        self.name = name
        self.quantity = quantity

    def __repr__(self) -> str:
        return f"Material(name={self.name!r}, quantity={self.quantity!r})"


class UpgradeCategory:
    """Represents a specific category of upgrade materials (e.g., Ascension, Skills)."""

    def __init__(self, page: Page, box_index: int) -> None:
        """Initialize an UpgradeCategory instance."""
        self._page = page
        self._box_index = box_index

    def name(self) -> str | None:
        """Return the name of this upgrade category."""
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
        """Retrieve a specific material by 1-based index in this category."""
        if self._page.locator(_UPGRADE_BOX_SELECTOR).count() == 0:
            return Material(None, None)

        box = self._page.locator(_UPGRADE_BOX_SELECTOR).nth(self._box_index)
        material = box.locator("li").nth(index - 1)

        return self._parse_material(material)

    @property
    def all(self) -> dict[int, Material]:
        """Retrieve all materials in this category as a 1-based dictionary."""
        if self._page.locator(_UPGRADE_BOX_SELECTOR).count() == 0:
            return {}
        box = self._page.locator(_UPGRADE_BOX_SELECTOR).nth(self._box_index)

        return {
            i: self._parse_material(mat) for i, mat in enumerate(box.locator("li").all(), 1)
        }


class UpgradeMaterials:
    """Interface to access various character upgrade material categories."""

    def __init__(self, page: Page) -> None:
        """Initialize UpgradeMaterials interface."""
        self._page = page

    @property
    def character_ascension(self) -> UpgradeCategory:
        """Access the character ascension material category."""
        return UpgradeCategory(self._page, 0)

    @property
    def skill_upgrades(self) -> UpgradeCategory:
        """Access the skill upgrade material category."""
        return UpgradeCategory(self._page, 1)


class Kit:
    """Primary entry point for accessing a character's complete kit information."""

    def __init__(self, page: Page) -> None:
        """Initialize Kit interface and navigate to the kit tab."""
        self._page = page
        self._page.locator(_MAIN_TAB_SELECTOR).nth(0).click()
        self.skills = Skills(self._page)
        self.resonance_chain = ResonanceChain(self._page)
        self.upgrade_materials = UpgradeMaterials(self._page)
