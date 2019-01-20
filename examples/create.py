import asyncio

import challonge


my_username = 'challonge_username'
my_api_key = 'challonge_api_key'


async def main(loop):
    my_user = await challonge.get_user(my_username, my_api_key)
    new_tournament = await my_user.create_tournament(name='my super tournament',
                                                     url='super-tournament-url')

    john = await new_tournament.add_participant('john')
    bob = await new_tournament.add_participant('bob')
    steve = await new_tournament.add_participant('steve')
    franck = await new_tournament.add_participant('franck')
    # or simply new_tournament.add_participants('john', 'bob', 'steve', 'franck')

    await new_tournament.start()

    matches = await new_tournament.get_matches()

    # match 1: john (p1) Vs bob (p2)
    await matches[0].report_winner(john, '2-0,1-2,2-1')
    # match 2: steve (p1) Vs franck (p2)
    await matches[1].report_winner(franck, '2-0,1-2,0-2')

    # finals: john (p1) Vs franck (p2)
    await matches[2].report_winner(franck, '2-1,0-2,1-2')

    await new_tournament.finalize()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
