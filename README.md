# ww_prydwen_api

A Python API for [prydwen.gg](https://www.prydwen.gg) Wuthering Waves data, built with Playwright.

Headless mode now works reliably by using `playwright-stealth` to get through Cloudflare detection.

Still early days — only characters are implemented so far, more coming.

## Installation

Activate virtual environment

```bash
python3 -m venv .env
source .env/bin/activate
pip install playwright playwright-stealth
playwright install
git clone https://github.com/theonuverse/ww_prydwen_api.git
```

Or optionally if you use Termux, you can use this Dockerfile together with PRoot Distro to automatically set the environment up.

```bash
FROM debian:13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN \
        apt-get update && apt-get upgrade -y && \
        apt-get install python3 python3-pip git -y && \
        pip install playwright playwright-stealth --break-system-packages && \
        playwright install-deps && \
        playwright install chromium

WORKDIR /root

RUN git clone https://github.com/theonuverse/ww_prydwen_api.git

CMD ["/bin/bash"]
```

Then build it, install it and run it.

```bash
pd build -t ww_prydwen_api:latest --install-as ww_prydwen_api --no-cache .
pd sh ww_prydwen_api
```

## Usage

```python
from ww_prydwen_api import Characters

with Characters() as chars:
    char = chars.get("iuno")

    # fetch character details
    print(char.name)
    print(char.introduction)
    print(char.role.all)  # dict of role(s), e.g. {1: "Main DPS"}

    # kit — skills (active / passive / concerto), all via properties
    skill = char.kit.skills.active.basic_attack
    print(skill.name, skill.description)
    print(char.kit.skills.active.resonance_skill.name)
    print(char.kit.skills.passive.forte_circuit.name)
    print(char.kit.skills.concerto.intro_skill.name)

    # multipliers still use the .get() method and .all property
    print(skill.multipliers.get(5))  # level 5 multiplier
    print(skill.multipliers.all)     # dict of all 10 levels

    # resonance chain
    print(char.kit.resonance_chain.get(1).name)  # S1
    print(char.kit.resonance_chain.all)          # dict of all 6 nodes

    # upgrade materials
    print(char.kit.upgrade_materials.character_ascension.all)  # dict of ascension materials
    print(char.kit.upgrade_materials.skill_upgrades.all)       # dict of skill upgrade materials

    # review
    review = char.review
    print(review.pros.get(1))   # first pro point
    print(review.cons.all)      # dict of all con points
    print(review.full_review)   # full text review

    # review ratings (tier list and value tier list — only populated if the
    # character actually has that rating; check available_roles first)
    print(review.ratings.tier_list.available_roles)  # e.g. {1: "DPS", 2: "Hybrid"}
    print(review.ratings.tier_list.dps.toa)          # DPS rating for Tower of Adversity
    print(review.ratings.value_tier_list.support.toa)  # Pull Value rating for Tower of Adversity

    # build
    build = char.build
    print(build.weapon_recommendations.all.name)        # dict of recommended weapon names
    print(build.weapon_recommendations.get(1).percentage.all)  # usage % breakdown
    print(build.echo_recommendations.all.name)          # dict of recommended echo set names
    print(build.echo_stats.all.stats)                    # dict of recommended main stats per cost slot
    print(build.echo_stats.substats)                     # recommended substat priority text
    print(build.endgame_stats.lines)                     # recommended endgame stats, as a list of lines

    # skill priority per role
    priority = build.skill_priority.get(1)
    print(priority.role)  # resolved role name, e.g. "Main DPS"
    print(priority.all)   # dict of skills in priority order
```

## What's implemented

- `Characters` — character pages
  - `name`, `introduction`, `role`
  - `kit` — Kit tab
    - `skills` — active / passive / concerto skills with multipliers
    - `resonance_chain` — all 6 sequence nodes
    - `upgrade_materials` — material requirements (ascension, skill upgrades, etc.)
  - `review` — Review tab
    - `pros` & `cons`
    - `full_review`
    - `ratings` — tier list and value tier list, plus `available_roles` to check which roles have ratings
  - `build` — Build tab
    - `weapon_recommendations` — recommended weapons, usage %, and write-ups
    - `echo_recommendations` — recommended echo sets, rank, and write-ups
    - `echo_stats` — recommended main stats per cost slot, plus substat priority
    - `endgame_stats` — recommended endgame stat targets
    - `skill_priority` — skill priority order per role

## What's coming

- Gameplay, Calculations
- Weapons
- Echoes
- Teams
- probably more idk

## Notes

- Always use `with Characters() as chars:` or manually call `.close()` at the end, otherwise the browser won't shut down cleanly
- Indexing is always 1-based so `get(1)` is the first, not `get(0)`
- Properties like `.all` return dictionaries populated with elements instead of requiring loops.
- Sections that don't exist for a given character (e.g. a role/rating a character doesn't have) raise `ValueError` rather than returning `None` — wrap in `try/except` when scraping many characters generically.
- I've also added docstrings everywhere, so your IDE should give you nice hints while coding!