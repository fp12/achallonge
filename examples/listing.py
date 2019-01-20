import asyncio

import challonge


my_username = 'challonge_username'
my_api_key = 'challonge_api_key'


async def main(loop):
    my_user = await challonge.get_user(my_username, my_api_key)
    my_tournaments = await my_user.get_tournaments()
    for t in my_tournaments:
        print(t.name, t.full_challonge_url)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
