import json
from http.cookiejar import LWPCookieJar
from time import sleep

import requests
import vrchatapi
from vrchatapi import *
from vrchatapi import configuration
from vrchatapi.api import *
from vrchatapi.exceptions import *
from vrchatapi.models import *
from vrchatapi.configuration import *

# Global variables for VRC credentials
VRC_USERNAME = ""
VRC_PASSWORD = ""
api_client = None
COOKIE_FILE = 'vrc_session.pkl'

def initializeCredentials(CREDS_FILE: str):
    global VRC_USERNAME, VRC_PASSWORD

    with open(CREDS_FILE, "r") as f:
        CREDS = json.loads(f.read())
        VRC_USERNAME = CREDS["VRC_USERNAME"]
        VRC_PASSWORD = CREDS["VRC_PASSWORD"]
def get_or_create_session():
    session = requests.Session()
    cookie_jar = LWPCookieJar(COOKIE_FILE)

    try:
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        session.cookies = cookie_jar
        print('loaded existing cookies')
        return session
    except FileNotFoundError:
        print('creating new cookies...')
        session.cookies = cookie_jar
        return session

def save_session(session):
    if isinstance(session.cookies, LWPCookieJar):
        session.cookies.save(ignore_discard=True, ignore_expires=True)
        print(f'saved existing cookies. {COOKIE_FILE}')

def main():
    global api_client

    initializeCredentials("credentials.json")

    configuration = vrchatapi.configuration.Configuration(
        username=VRC_USERNAME,
        password=VRC_PASSWORD,
    )
    api_client = vrchatapi.ApiClient(configuration)
    api_client.user_agent = f'Mozilla/5.0 {VRC_USERNAME}'  # Optional: uncomment if needed

    auth_api = authentication_api.AuthenticationApi(api_client)

    try:
        current_user1 = auth_api.get_current_user()
    except UnauthorizedException as e:
        # 2FA is required
        if '2 Factor Authentication' in str(e.reason):
            print('2FA code required (Authenticator app)')
            try:
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input('Enter the 2FA code...')))
                current_user1 = auth_api.get_current_user()
            except Exception as e2:
                print(f'Failed to verify 2FA code. exception: {e2}')
                return
        else:
            # Email 2FA
            print('2FA email code required')
            try:
                auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input('Enter the 2FA code from email...')))
                current_user1 = auth_api.get_current_user()
            except Exception as e2:
                print(f'Failed to verify email 2FA code. exception: {e2}')
                return
    except vrchatapi.ApiException as e:
        print(f'API Error: {e}')
        return

    print(f'Logged in as: {current_user1.username} ID: {current_user1.id}')

    #export all of my data in vrc
    current_user1:User = current_user1
    users_api = UsersApi(api_client)
    current_user1_obj = users_api.get_user(current_user1.id)
    with open('data-of-myself.txt', 'w') as f:
        f.write(str(current_user1_obj))

    wait1min()

def wait1min():
    print('Waiting 1 minute...')
    sleep(60)
if __name__ == '__main__':
    main()