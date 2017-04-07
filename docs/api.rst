.. currentmodule:: challonge


API
===


User
----

.. autofunction:: get_user

.. autoclass:: User
    :members:


Tournament
----------

.. class:: TournamentType
	
	.. attribute:: double_elimination
	
	.. attribute:: single_elimination
	
	.. attribute:: round_robin
	
	.. attribute:: swiss 


.. class:: DoubleEliminationEnding

	.. attribute:: default

		give the winners bracket finalist two chances to beat the losers bracket finalist.
	.. attribute:: single_match

		create only one grand finals match.
	.. attribute:: no_grand_finals

		don't create a finals match between winners and losers bracket finalists.
	

.. autoclass:: challonge.Tournament
    :members:
    :member-order: bysource


Participant
-----------

.. autoclass:: challonge.Participant
    :members:
    :member-order: bysource


Match
-----

.. class:: MatchState
	
	.. attribute:: all_

	.. attribute:: open_
	
	.. attribute:: pending
	
	.. attribute:: complete


.. autoclass:: challonge.Match
    :members:
    :member-order: bysource


Attachment
----------

.. autoclass:: challonge.Attachment
    :members:
    :member-order: bysource


Exceptions
----------

.. autoclass:: challonge.APIException
