import os
import json
import requests
import logging

class Config:
    def __init__(self, config_file):
        self._MIDDLEWARE_USERNAME_UYA=os.getenv("MIDDLEWARE_USERNAME_UYA")
        self._MIDDLEWARE_PASSWORD_UYA=os.getenv("MIDDLEWARE_PASSWORD_UYA")
        self._MIDDLEWARE_ENDPOINT_UYA=os.getenv("MIDDLEWARE_ENDPOINT_UYA")

        self._local_headers = {}

        if config_file == None:
            # Use environment vars
            self._set_env_vars()
        else:
            self._set_from_file(config_file)

    def _set_env_vars(self):
        raw_dict = {
            "local": False,
            "profile_id": int(os.getenv("PROFILE_ID")),
            "bot_mode": os.getenv("BOT_MODE"),
            "account_id": int(os.getenv("ACCOUNT_ID")),
            "account_name": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
            "world_id": int(os.getenv("WORLD_ID")),
            "mas_ip": os.getenv("MAS_IP"),
            "mas_port": int(os.getenv("MAS_PORT")),
            "mls_ip": os.getenv("MLS_IP"),
            "mls_port": int(os.getenv("MLS_PORT")),
            "timeout": 60,
            "mls_log_level": logging.DEBUG,
            "mas_log_level": logging.DEBUG,
            "dmetcp_log_level": logging.DEBUG,
            "dmeudp_log_level": logging.DEBUG,
            "model_log_level": logging.DEBUG,
        }

        for key, value in raw_dict.items():
            self.__dict__[key] = value

    def _set_from_file(self, config_file):
        # This will always be local debugging
        with open(config_file, 'r') as f:
            result = json.loads(f.read())
            result['local'] = True
            for key, value in result.items():
                if 'log_level' in key:
                    if value == 'debug':
                        value = logging.DEBUG
                    elif value == 'info':
                        value = logging.INFO

                self.__dict__[key] = value
        self._authenticate()

        self.world_id = self._get_active_games(result['game_name_to_join'])

    def _authenticate(self):
        data = {
        "AccountName": self._MIDDLEWARE_USERNAME_UYA,
        "Password": self._MIDDLEWARE_PASSWORD_UYA
        }
        response = requests.post(self._MIDDLEWARE_ENDPOINT_UYA + "Account/authenticate", json=data, verify=False)
        if response.status_code == 200:
            print("Authenticated API!")
            token = response.json()["Token"]
            self._local_headers["UYA"] = { "Authorization": f"Bearer {token}" }
            return True
        else:
            print(response.status_code)
            print("ERROR AUTHENTICATING!")
            return None

    def _get_active_games(self, game_name_to_join):    
        route =  f"api/Game/list"
        response = requests.get(self._MIDDLEWARE_ENDPOINT_UYA + route, headers=self._local_headers["UYA"], verify=False)

        if response.status_code == 200:
            games = response.json()
            for game in games:
                if game_name_to_join in game['GameName']:
                    print("ID:", game['Id'], "GameId:", game['GameId'])
                    return game['GameId']
            raise Exception("Unknown game found.")

    def __str__(self):
        result = 'Config; '
        for attr in dir(self):
            if not attr.startswith('_'):
                val = eval(f"self.{attr}")
                result += f'{attr}:{val} '
        return result