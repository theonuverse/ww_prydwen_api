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

Or optionally if you use Termux, you can use this Dockerfile together with PRoot Distro to automatically set the environment up.

```bash
FROM debian:13

ENV DEBIAN_FRONTEND=noninteractive

RUN \
        apt-get update && apt-get upgrade -y && \
        apt-get install python3 python3-pip git neovim -y && \
        pip install playwright --break-system-packages && \
        playwright install-deps && \
        playwright install chromium

WORKDIR /root

RUN git clone https://github.com/theonuverse/ww_prydwen_api.git

CMD ["/bin/bash"]
```

Then build it, install it and run it.

```bash
pd build -t ww_prydwen_api --install-as ww_prydwen_api --no-cache .
pd sh ww_prydwen_api --isolated
```

## Usage

```python
from ww_prydwen_api import Characters

with Characters() as chars:
    char = chars.get("aemeath")

    # get a skill (1-based index)
    skill = char.kit.skills.active(1)
    print(skill.name)
    print(skill.description)
    print(skill.multipliers.get(5))  # level 5 multiplier
    print(skill.multipliers.all())   # all 10 levels

    # resonance chain
    chain = char.kit.resonance_chain
    print(chain.get(1).name)  # S1
    print(chain.all)          # dict of all 6 nodes

    # upgrade materials
    mats = char.kit.upgrade_materials.character_ascension
    print(mats.get(1).name)   # first material required for ascension
    print(mats.all)           # dict of all ascension materials
    
    # review
    review = char.review
    print(review.pros.get(1)) # first pro point
    print(review.cons.all)    # dict of all con points
    print(review.full_review) # full text review
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

## What's coming

- Review (Ratings) Build, Gameplay, Calculations tabs
- Weapons
- Echoes
- Teams
- Tier lists
- probably more idk

## Notes

- Always use `with Characters() as chars:` or manually call `.close()` at the end, otherwise the browser won't shut down cleanly
- Indexing is always 1-based so `active(1)` is the first skill, not `active(0)`
- Properties like `.all` return dictionaries populated with elements instead of requiring loops.
- I've also added docstrings everywhere, so your IDE should give you nice hints while coding!
