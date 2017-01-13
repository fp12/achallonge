.. achallonge documentation master file, created by
   sphinx-quickstart on Thu Dec 29 21:19:51 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

achallonge
==========

async challonge for python 3.5+!

.. _GitHub: https://github.com/fp12/achallonge


Features
--------

- More than a just a wrapper to the Challonge API
- Natural structures to work with (:class:`User`, :class:`Tournament`, :class:`Participant`, :class:`Match`, :class:`Attachment`)
- No knowledge of the Challonge API is required, thanks to extensively documented library


Getting Started
---------------

Simple example:

.. literalinclude:: ../examples/listing.py


Dependencies
------------

- python 3.5+
- aiohttp
    - cchardet
    - aiodns


Author and License
------------------

The ``achallonge`` package is written by Fabien Poupineau (fp12).

It's distributed under the *MIT* license.

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
