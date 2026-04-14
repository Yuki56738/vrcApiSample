from vrchatapi import api_client

from auth_to_vrc import *

def main():
    print('Welcome to the UNDERGROUND...')
    auth_api = loadCookieAndAuth()
    current_user = auth_api.get_current_user()
    print("Logged in as:", current_user.display_name)
    wait1min()

if __name__ == "__main__":
    main()