import asyncio

from vrchatapi import api_client
from auth_to_vrc import *
from vrchatapi.api import *
from vrchatapi.api.friends_api import *

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('app.log'),
                    ])
logging.getLogger('urllib3').setLevel(logging.DEBUG)
logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.DEBUG)


API_USER_AGENT = "VrcApiAppForMe/0.1 contact@yukiito.dev"


def main():
    print('Welcome to the UNDERGROUND...')
    logging.info('Logging into VRChat API...')
    auth_api = AuthWithSavedCookie()
    auth_api.user_agent = API_USER_AGENT
    current_user = auth_api.get_current_user()
    if not current_user:
        logging.warning('Failed to authenticate with saved cookie. Trying to new session...')
        auth_api = authAndStoreCookie()
        auth_api.user_agent = API_USER_AGENT

        current_user = auth_api.get_current_user()
        print("Logged in as:", current_user.display_name)
    get_online_friends(auth_api ,current_user)
    wait1min()

def get_online_friends(auth_api: AuthenticationApi ,current_user: CurrentUser):
    logging.info('Getting online friends...')
    try:
        current_user.user_agent = API_USER_AGENT
        friends:list = current_user.online_friends
        logging.info('writing online friends to file...')
        with open('friends-online.txt', 'w') as f:
            f.writelines(str(friends))
    except Exception as e:
        logging.error(f'Failed to get online friends: {e}')
        return e

    friends_api = FriendsApi(auth_api)
    for x in friends:
        print(x)

    return friends



def get_online_friends_old(auth_api: AuthenticationApi, current_user: CurrentUser):
    logging.info('Getting friends...')
    try:
        friends = current_user.friends
        # friends = friends_api.get_friends()
        with open('friends.txt', 'w') as f:
            f.writelines(str(friends))
    except Exception as e:
        logging.error(f'Failed to get friends: {e}')
        return e

def get_friends(auth_api: AuthenticationApi, current_user: CurrentUser):
    logging.info('Getting friends...')
    try:

        auth_api.user_agent = API_USER_AGENT

        friends_api = FriendsApi(auth_api)
        friends = friends_api.get_friends()
        with open('friends-all.txt', 'w') as f:
            f.writelines(str(friends))
    except Exception as e:
        logging.error(f'Failed to get friends: {e}')
        return e


if __name__ == "__main__":
    main()
