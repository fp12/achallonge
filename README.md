# achallonge
*Async Challonge for Python 3.5+*

[![Build Status](https://travis-ci.org/fp12/achallonge.svg?branch=master)](https://travis-ci.org/fp12/achallonge)

Modern library that is more than just a wrapper for the Challonge web API


# Requirements

* `aiohttp`

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
		print(t.id) # 3272
		print(t.name) # My Awesome Tournament
		print(t.status) # open

    # Retrieve the participants for a given tournament.
    participants = await tournaments[0].get_participant()
    print(len(participants)) # 13
```