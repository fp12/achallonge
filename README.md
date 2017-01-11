# achallonge
*async Challonge for Python 3.5+*

[![Build Status](https://travis-ci.org/fp12/achallonge.svg?branch=master)](https://travis-ci.org/fp12/achallonge)
[![Documentation Status](https://readthedocs.org/projects/achallonge/badge/?version=latest)](http://achallonge.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/fp12/achallonge/badge.svg?branch=master)](https://coveralls.io/github/fp12/achallonge?branch=master)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/cd2c13493bdf461695ada40356a9d3a1/badge.svg)](https://www.quantifiedcode.com/app/project/cd2c13493bdf461695ada40356a9d3a1)


Modern library that is more than just a wrapper for the Challonge web API


# Requirements

* `aiohttp`
    * `cchardet` faster replacement for chardet, as mentionned on the aiohttp page
    * `aiodns` for speeding up DNS resolving, highly recommended by aiohttp

# Python version support

* `3.5`
* `3.6`

# Installation

    pip install -e git+http://github.com/fp12/achallonge#egg=achallonge
    
# Usage

```python
import challonge

async def pychallonge_async()
    # Log in into Challonge with your [CHALLONGE! API credentials](https://challonge.com/settings/developer).
    user = challonge.get_user('your_challonge_username', 'your_api_key')

    # Retrieve your tournaments
    tournaments = await user.get_tournaments()

    # Tournaments, matches, and participants are all represented as Python classes
    for t in tournaments:
		print(t.id)  # 3272
		print(t.name)  # 'My Awesome Tournament'
		print(t.status)  # 'open'

    # Retrieve the participants for a given tournament.
    participants = await tournaments[0].get_participants()
    print(len(participants)) # 13
```

# Documentation

The full documentation can be found on [Read the docs](http://achallonge.readthedocs.io/en/latest/index.html)

# Author / License

Distributed under MIT license. See `LICENSE` for details

Fabien Poupineau (fp12) - 2017
Twitter: [@fp12gaming](https://twitter.com/fp12gaming)
Join the [Discord Server](https://discord.gg/KSRxBav) and discuss about this lib!
