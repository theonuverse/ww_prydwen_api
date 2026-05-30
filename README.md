# ww_prydwen_api

A Python API for [prydwen.gg](https://www.prydwen.gg) Wuthering Waves data, built with Playwright.

Still early days — only characters are implemented so far, more coming.

## Installation

Activate virtual environment

```bash
python3 -m venv .env
source .env/bin/activate
pip install playwright
playwright install
git clone https://github.com/theonuverse/ww_prydwen_api.git
```

## Usage

```python
from ww_prydwen_api import Characters

with Characters() as chars:
    char = chars.get("https://www.prydwen.gg/wuthering-waves/characters/aemeath")

    # get a skill (1-based index)
    skill = char.kit().skills().active(1)
    print(skill.name)
    print(skill.description)
    print(skill.multipliers.get(5))  # level 5 multiplier
    print(skill.multipliers.all())   # all 10 levels

    # resonance chain
    chain = char.kit().resonance_chain()
    print(chain.get(1).name)  # S1
    print(chain.all())        # all 6 nodes
```

## What's implemented

- `Characters` — character pages
  - `kit()` — Kit tab
    - `skills()` — active / passive / concerto skills with multipliers
    - `resonance_chain()` — all 6 sequence nodes

## What's coming

- Review, Build, Gameplay, Calculations tabs
- Weapons
- Echoes
- Teams
- Tier lists
- probably more idk

## Notes

- Always use `with Characters() as chars:` or manually call `.close()` at the end, otherwise the browser won't shut down cleanly
- Indexing is always 1-based so `active(1)` is the first skill, not `active(0)`
