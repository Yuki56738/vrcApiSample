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

# Global variables for VRC credentials
VRC_USERNAME = ""
VRC_PASSWORD = ""


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
        api_client.user_agent = f'Mozilla/5.0 {VRC_USERNAME}'
        auth_api = authentication_api.AuthenticationApi(api_client)

        try:
            current_user = auth_api.get_current_user()
        except UnauthorizedException as e:
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
    return api_client


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


def loadCookieAndAuth():
    initializeCredentials("credentials.json")

    configuration = vrchatapi.Configuration(
        username=VRC_USERNAME,
        password=VRC_PASSWORD,
    )

    with open('cookies.json', 'r') as f:
        cookies_to_saved = {}
        cookies_to_saved.update(json.JSONDecoder().decode(f.read()))

    with vrchatapi.ApiClient(configuration) as api_client:
        api_client.user_agent = f'Mozilla/5.0 {VRC_USERNAME}'
        api_client.rest_client.cookie_jar.set_cookie(
            makeCookie('auth', cookies_to_saved.get("auth")))
        api_client.rest_client.cookie_jar.set_cookie(
            makeCookie('twoFactorAuth', cookies_to_saved.get("2fa")))
        auth_api = authentication_api.AuthenticationApi(api_client)
        current_user = auth_api.get_current_user()
        print("Logged in with saved cookies as:", current_user.display_name)
    return auth_api


def wait1min():
    print('Waiting 1 minutes...')
    sleep(60)


if __name__ == '__main__':
    authAndStoreCookie()
    wait1min()
