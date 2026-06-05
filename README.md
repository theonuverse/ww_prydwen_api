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
        apt-get install python3 python3-pip git neovim -y && \
        pip install playwright playwright-stealth --break-system-packages && \
        playwright install-deps && \
        playwright install chromium

WORKDIR /root

RUN git clone https://github.com/theonuverse/ww_prydwen_api.git

CMD ["/bin/bash"]
```

Then build it, install it and run it.

```bash
pd build -t ww_prydwen_api:latest -o ww_prydwen_api.tar.gz .
pd install ./ww_prydwen_api.tar.gz
pd sh ./ww_prydwen_api
```

## Usage

```python
from ww_prydwen_api import Characters

with Characters() as chars:
    char = chars.get("aemeath")

    # fetch character details
    print(char.name)
    print(char.introduction)

    # get a skill (Now uses properties instead of indexes!)
    skill = char.kit.skills.active.basic_attack
    print(skill.name)
    print(skill.description)
    
    # you can also get other active skills
    print(char.kit.skills.active.resonance_skill.name)
    print(char.kit.skills.active.resonance_liberation.name)
    
    # passive and concerto skills
    print(char.kit.skills.passive.forte_circuit.name)
    print(char.kit.skills.concerto.intro_skill.name)
    
    # multipliers still use the .get() method and .all property
    print(skill.multipliers.get(5))  # level 5 multiplier
    print(skill.multipliers.all)     # dict of all 10 levels

    # resonance chain
    chain = char.kit.resonance_chain
    print(chain.get(1).name)  # S1
    print(chain.all)          # dict of all 6 nodes

    # upgrade materials
    mats = char.kit.upgrade_materials.character_ascension
    print(mats.get(1).name)   # first material required for ascension
    print(mats.all)           # dict of all ascension materials
    
    skill_mats = char.kit.upgrade_materials.skill_upgrades
    print(skill_mats.all)     # dict of all skill upgrade materials
    
    # review
    review = char.review
    print(review.pros.get(1)) # first pro point
    print(review.cons.all)    # dict of all con points
    print(review.full_review) # full text review
    
    # review ratings (Tier lists and Value Tier lists)
    ratings = review.ratings
    print(ratings.tier_list.dps.toa)       # DPS rating for Tower of Adversity
    print(ratings.tier_list.hybrid.whiwa)  # Hybrid rating for Whimpering Wastes
    print(ratings.value_tier_list.support.toa) # Pull Value rating for Tower of Adversity
```

## What's implemented

- `Characters` — character pages
  - `name`, `introduction`
  - `kit` — Kit tab
    - `skills` — active / passive / concerto skills with multipliers
    - `resonance_chain` — all 6 sequence nodes
    - `upgrade_materials` — material requirements (ascension, skill upgrades, etc.)
  - `review` — Review tab
    - `pros` & `cons`
    - `full_review`
    - `ratings` — Tier list and Value tier list support

## What's coming

- Build, Gameplay, Calculations tabs
- Weapons
- Echoes
- Teams
- probably more idk

## Notes

- Always use `with Characters() as chars:` or manually call `.close()` at the end, otherwise the browser won't shut down cleanly
- Indexing is always 1-based so `get(1)` is the first, not `get(0)`
- Properties like `.all` return dictionaries populated with elements instead of requiring loops.
- I've also added docstrings everywhere, so your IDE should give you nice hints while coding!
