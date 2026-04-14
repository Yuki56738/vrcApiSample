import json
from time import sleep

import vrchatapi
from vrchatapi import *
from vrchatapi import configuration
from vrchatapi.api import *
from vrchatapi.exceptions import *
from vrchatapi.models import *
from vrchatapi.configuration import *

def initializeCredentials(CREDS_FILE: str):
    CREDS_FILE = "credentials.json" #Default value for CREDS_FILE var
    global VRC_USERNAME, VRC_PASSWORD

    VRC_USERNAME = ""
    VRC_PASSWORD = ""
    with open(CREDS_FILE, "r") as f:
        CREDS = json.loads(f.read())
        VRC_USERNAME = CREDS["VRC_USERNAME"]
        VRC_PASSWORD = CREDS["VRC_PASSWORD"]

def main():
    initializeCredentials("credentials.json")

    configuration = vrchatapi.configuration.Configuration(
        username=VRC_USERNAME,
        password=VRC_PASSWORD,
    )
    api_client = vrchatapi.ApiClient(configuration)
    api_client.user_agent= f'Mozilla/5.0 {VRC_USERNAME}'

    auth_api = authentication_api.AuthenticationApi(api_client)
    try:
        current_user1 = auth_api.get_current_user()
    except UnauthorizedException as e:
        if e.status == 200:
            if '2 Factor Authentication' in e.reason:
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input('Enter the 2FA code...')))
            else:
                auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input('Enter the 2FA code you got from E-mail...')))

        else:
            print(f'Auth failed. reason: {e.reason}')
    except vrchatapi.ApiException as e:
        print(f'API Error: {e}')
    greeting(auth_api)

    # get_all_of_my_data(auth_api)

    wait1min()

def get_all_of_my_data(auth_api: AuthenticationApi):
    print('getting all my data...')
    current_user1 = auth_api.get_current_user()
    user_api1 = UsersApi(auth_api)
    result1 = user_api1.get_user(current_user1.id)
    with open('my_data.json', 'w') as f:
        f.write(json.dumps(result1))

def greeting(auth_api: authentication_api.AuthenticationApi):
    current_user1 = auth_api.get_current_user()
    print(f'Logged in as: {current_user1.username} ID: {current_user1.id}')

def wait1min():
    print('Waiting 1 minute...')
    sleep(60)
if __name__ == '__main__':
    main()