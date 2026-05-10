import asyncio
import datetime
import os

from vrchatapi import api_client
from auth_to_vrc import *
from vrchatapi.api import *
from vrchatapi.api.friends_api import *
from vrchatapi.models.friend_status import *
from vrchatapi.models import *

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        # logging.FileHandler('app.log'),
                    ])
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.DEBUG)

API_USER_AGENT = "VrcApiAppForMe/0.1 contact@yukiito.dev"


def main():
    print('Welcome to the UNDERGROUND...')
    logging.info('Logging into VRChat API...')
    auth_api = AuthWithSavedCookie()
    auth_api.user_agent = API_USER_AGENT
    current_user: CurrentUser = auth_api.get_current_user()
    if not current_user:
        logging.warning('Failed to authenticate with saved cookie. Trying to new session...')
        auth_api = authAndStoreCookie()
        auth_api.user_agent = API_USER_AGENT

        current_user = auth_api.get_current_user()

    api_client = auth_api.api_client
    print(f'Logged in as: {current_user.display_name}')
    logging.debug(f'Last login: {current_user.last_login}')
    print(f'Last login: {current_user.last_login.strftime('%a %b %d %H:%M:%S %Y')} from 192.168.1.1')

    try:
        friends = get_online_friends(auth_api, current_user)
    except Exception as e:
        print(f'Failed to get online friends: {e}')
        return False

    # delete if file friends-status.txt exists
    logging.debug('Removing file friends-status.txt if it exists...')
    try:
        os.remove('friends-status.txt')
    except Exception as e:
        logging.debug(f'Failed to remove file friends-status.txt: {e}')
        pass
    friendStatusesDict = {}
    for friend in friends:
        friend: LimitedUserFriend
        if not friend.platform == 'web' and not friend.location == 'private' and not friend.location == 'offline' and not friend.location == 'traveling':
            friend_statuses = f'{friend.status}, {friend.status_description}, {friend.display_name}}'
            friendLastLogin: datetime= friend.last_login
            # print(f'{friend.status}, {friend.status_description}, {friend.display_name}')
            print(friend_statuses)
            try:
                world_obj = get_world_obj(api_client=api_client, current_user=current_user, world_id=friend.location)
            except Exception as e:
                print(f'Failed to get world obj: {e}')
                continue
            friend_world_statuses = f'in {world_obj.name}, {world_obj.tags}'
            # print(f'in {world_obj.name}, {world_obj.tags}')
            print(friend_world_statuses)
            try:
                instance_obj = get_instance_obj(api_client=api_client, current_user=current_user,
                                                instance_id=friend.location)
            except Exception as e:
                print(f'Failed to get instance obj: {e}')
                continue
            friend_instance_statuses = f'instance: {instance_obj.display_name}, private: {instance_obj.private}, {instance_obj.type}'
            print(friend_instance_statuses)
            with open('friends-status.txt', 'a') as f:
                f.write(friend_statuses + '\n')
                f.write(friend_world_statuses + '\n')
                f.write(friend_instance_statuses + '\n')

            # print(f'instance: {instance_obj.display_name}, private: {instance_obj.private}, {instance_obj.type}')

    wait1min()




def get_user_obj(api_client: ApiClient, user_id: str) -> User:
    logging.debug('Getting user obj...')
    users_api = UsersApi(api_client)
    user_obj = users_api.get_user(user_id=user_id)
    return user_obj


def get_world_obj(api_client: ApiClient, current_user: CurrentUser, world_id: str) -> World:
    logging.debug('Getting world obj...')
    text = world_id
    match = re.match(r'^[^:]*', text)
    world_real_id = match.group()
    # instance_real_id = re.match(, world_id)
    worlds_api = WorldsApi(api_client)
    world_obj = worlds_api.get_world(world_id=world_real_id)
    logging.debug(f'Got world obj: {world_obj.name}')
    return world_obj


def get_instance_obj(api_client: ApiClient, current_user: CurrentUser, instance_id: str) -> Instance:
    logging.debug('Getting instance obj...')
    text = instance_id
    match = re.search(r':(.*)$', text)
    if match:
        instance_real_id = match.group(1)
    else:
        return False
    text = instance_id
    match = re.match(r'^[^:]*', text)
    world_real_id = match.group()

    instances_api = InstancesApi(api_client)
    instance_obj = instances_api.get_instance(world_id=world_real_id, instance_id=instance_real_id)
    return instance_obj


def get_online_friends(auth_api: AuthenticationApi, current_user: CurrentUser):
    logging.info('Getting online friends...')
    try:
        current_user.user_agent = API_USER_AGENT

        api_client = auth_api.api_client
        # api_client.user_agent = API_USER_AGENT
        api_client.user_agent = API_USER_AGENT
        friends_api = FriendsApi(api_client)
        # friends = friends_api.get_friends()
        friends = friends_api.get_friends(offline=False)
        logging.info('writing friends to file friends-online.txt...')
        with open('friends-online.txt', 'w') as f:
            f.writelines(str(friends))
        logging.info(f'You have {len(friends)} online friends')
        return friends
    except Exception as e:
        logging.error(f'Failed to get online friends: {e}')
        return e


if __name__ == "__main__":
    main()
