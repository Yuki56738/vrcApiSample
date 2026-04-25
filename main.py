import asyncio

from vrchatapi import api_client
from auth_to_vrc import *
from vrchatapi.api import *
from vrchatapi.api.friends_api import *
def main():
    print('Welcome to the UNDERGROUND...')
    auth_api = AuthWithSavedCookie()
    # current_user = auth_api.get_current_user()
    if not auth_api:
        print(f'Failed to authenticate with VRChat API.')
        print('Trying with new session...')
        auth_api = authAndStoreCookie()
        current_user = auth_api.get_current_user()
        print("Logged in as:", current_user.display_name)

    # get_online_friends(auth_api, current_user)
    wait1min()

def get_online_friends(auth_api: AuthenticationApi, current_user: CurrentUser):
    print('hit get online friends')
    friends_api = FriendsApi()
    print('Getting friends from VRChat API...')
    friends = friends_api.get_friends()
    for friend in friends:
        print(f'{friend.display_name}: {friend.id}')


if __name__ == "__main__":
    main()
