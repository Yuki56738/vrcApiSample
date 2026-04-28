import json
from time import sleep

import vrchatapi
from vrchatapi.api import *
from vrchatapi.exceptions import *
from vrchatapi.models import *
from vrchatapi.models.two_factor_auth_code import *
from vrchatapi.models.two_factor_email_code import *
from http.cookiejar import Cookie
from vrchatapi.api import authentication_api

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('api.log'),
                    ])
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.DEBUG)


# Global variables for VRC credentials
VRC_USERNAME = ""
VRC_PASSWORD = ""

API_USER_AGENT = "VrcApiAppForMe/0.1 contact@yukiito.dev"

def initializeCredentials(CREDS_FILE: str):
    global VRC_USERNAME, VRC_PASSWORD

    with open(CREDS_FILE, "r") as f:
        CREDS = json.loads(f.read())
        VRC_USERNAME = CREDS["VRC_USERNAME"]
        VRC_PASSWORD = CREDS["VRC_PASSWORD"]


def authAndStoreCookie():
    initializeCredentials("credentials.json")

    configuration = vrchatapi.Configuration(
        username=VRC_USERNAME,
        password=VRC_PASSWORD,
    )

    with vrchatapi.ApiClient(configuration) as api_client:
        # api_client.user_agent = f'Mozilla/5.0 {VRC_USERNAME}'
        api_client.user_agent = API_USER_AGENT
        auth_api = authentication_api.AuthenticationApi(api_client)

        try:
            current_user = auth_api.get_current_user()
        except UnauthorizedException as e:
            logging.debug(f'api res body: {e.body}')
            if e.status == 200:
                if "Email 2 Factor Authentication" in e.reason:
                    auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
                elif "2 Factor Authentication" in e.reason:
                    auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
                current_user = auth_api.get_current_user()
            else:
                print("Exception when calling API: %s\n", e)
        except vrchatapi.ApiException as e:
            print("Exception when calling API: %s\n", e)

        cookie_jar = api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
        print("Logged in as:", current_user.display_name)
        with open('cookies.json', 'w') as f:
            cookies_to_save = {
                'auth': cookie_jar['auth'].value,
                '2fa': cookie_jar['twoFactorAuth'].value,
            }
            print('saving cookies to file...')
            f.writelines(json.JSONEncoder().encode(cookies_to_save))
    return auth_api


def makeCookie(name, value):
    return Cookie(0, name, value,
                  None, False,
                  "api.vrchat.cloud", True, False,
                  "/", False,
                  False,
                  173106866300,
                  False,
                  None,
                  None, {})


def AuthWithSavedCookie():
    initializeCredentials("credentials.json")

    configuration = vrchatapi.Configuration(
        username=VRC_USERNAME,
        password=VRC_PASSWORD,
    )
    try:
        with open('cookies.json', 'r') as f:
            cookies_to_saved = {}
            cookies_to_saved.update(json.JSONDecoder().decode(f.read()))
    except FileNotFoundError:
        logging.error('cookies.json not found')
        return False
    logging.info('authenticating with saved cookies...')
    with vrchatapi.ApiClient(configuration) as api_client:
        try:
            api_client.rest_client.cookie_jar.set_cookie(
                makeCookie('auth', cookies_to_saved.get("auth")))
            api_client.rest_client.cookie_jar.set_cookie(
                makeCookie('twoFactorAuth', cookies_to_saved.get("2fa")))
            api_client.user_agent = API_USER_AGENT
        except Exception as e:
            logging.error(f"Exception when calling AuthenticationApi with saved cookies: {e}")
            return False
        try:
            auth_api = authentication_api.AuthenticationApi(api_client)
            current_user = auth_api.get_current_user()
            logging.info(f"Logged in with saved cookies as: {current_user.display_name}")
        except Exception as e:
            logging.error(f"Exception when calling AuthenticationApi with saved cookies: {e}")
            return False
    return auth_api


def wait1min():
    print('Waiting 1 minutes...')
    sleep(60)

if __name__ == '__main__':
    pass

