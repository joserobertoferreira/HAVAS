from http import HTTPStatus

from auth.auth import Auth
from config import settings


class AuthenticationService:
    def __init__(self):
        self.auth = Auth(settings.SERVER_BASE_ADDRESS)

    def login(self, username: str, password: str) -> dict:
        login_data = self.auth.login(username, password)

        if login_data['HttpStatus'] == HTTPStatus.OK:
            login_data['headers'] = {
                'Authorization': f'Bearer {login_data["Token"]}',
                'Content-type': 'application/json',
            }

            return login_data
        else:
            print('Authentication failed.')
            return {}

    def logout(self, token: str) -> None:
        self.auth.logout(token)
