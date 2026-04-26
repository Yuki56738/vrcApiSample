import asyncio

from vrchatapi import api_client
from auth_to_vrc import *
from vrchatapi.api import *
from vrchatapi.api.friends_api import *
from vrchatapi.models.friend_status import *
from vrchatapi.models import *

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
    api_client = auth_api.api_client

    friends = get_online_friends(auth_api ,current_user)
    for friend in friends:
        friend: LimitedUserFriend
        # print(friend.status, friend.display_name)
        if not friend.platform == 'web' and not friend.location == 'private' and not friend.location == 'offline':
            print(f'{friend.status}, {friend.status_description}, {friend.display_name}')
            world_obj = get_world_obj(api_client=api_client, current_user=current_user, world_id=friend.location)
            print(f'in {world_obj.name}, {world_obj.tags}')
            instance_obj = get_instance_obj(api_client=api_client, current_user=current_user, instance_id=friend.location)
            print(f'instance: {instance_obj.display_name}, private: {instance_obj.private}, {instance_obj.type}')
            # print(f'in {get_world_obj(api_client=api_client, current_user=current_user, world_id=friend.location)}')
            # print(f'in {get_world_obj(api_client=api_client, current_user=current_user, world_id=friend.location).name}')
            # print(f'in {get_world_obj(api_client=api_client, current_user=current_user, world_id=friend.location)}')

# def get_my_friends(api_client: ApiClient, current_user: CurrentUser):
#     logging.info('Getting my friends...')
#     friends_api = FriendsApi(api_client)

#Doesnt work
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

#Doesnt work
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

# def get_location_obj(world_id: str,instance_id: str, api_client: ApiClient, current_user: CurrentUser):
#     logging.info('Getting location...')
#     instances_api = InstancesApi(api_client)
#     ins: Instance = instances_api.get_instance(world_id=world_id ,instance_id=instance_id)
#     logging.debug(ins.name)
#     return ins


def get_online_friends(auth_api: AuthenticationApi ,current_user: CurrentUser):
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
        # for x in friends:
        #     print(x.id, x.display_name)
        # friends:list = current_user.online_friends
        # logging.info('writing online friends to file...')
        # with open('friends-online.txt', 'w') as f:
        #     f.writelines(str(friends))
    except Exception as e:
        logging.error(f'Failed to get online friends: {e}')
        return e
    # api_client = auth_api.api_client
    # for x in friends:
    #     print(x)
    #     print(x.display_name)




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
