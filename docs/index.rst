.. achallonge documentation master file, created by
   sphinx-quickstart on Thu Dec 29 21:19:51 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

achallonge
==========

async challonge for python 3.5+!

.. _GitHub: https://github.com/fp12/achallonge
.. highlight:: python


Features
--------

- More than a just a wrapper to the Challonge API
- Natural structures to work with (:class:`User`, :class:`Tournament`, :class:`Participant`, :class:`Match`, :class:`Attachment`)
- No knowledge of the Challonge API is required, thanks to extensively documented library


Getting Started
---------------

Simple example::

    import challonge
    import asyncio

    my_username = 'challonge_username'
    my_api_key = 'challonge_api_key'

    async def main(loop):
    my_user = challonge.get_user(my_username, my_api_key)
    my_tournaments = await my_user.get_tournaments()
    for t in my_tournaments:
        print(t.name)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))



Dependencies
------------

- python 3.5+
- aiohttp
    - cchardet
    - aiodns


Author and License
------------------

The ``achallonge`` package is written by Fabien Poupineau (fp12).

It's covered under the *MIT* license.

Feel free to improve this package and send a pull request to GitHub_.



.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   api
   examples



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
