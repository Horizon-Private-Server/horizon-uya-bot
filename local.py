import os
import traceback
import os
import requests
import random
import json
import datetime
import traceback
import constants
import urllib3

MIDDLEWARE_USERNAME_UYA=os.getenv("MIDDLEWARE_USERNAME_UYA")
MIDDLEWARE_PASSWORD_UYA=os.getenv("MIDDLEWARE_PASSWORD_UYA")
MIDDLEWARE_ENDPOINT_UYA=os.getenv("MIDDLEWARE_ENDPOINT_UYA")

api = 'UYA'
headers = {}

def authenticate():
  global headers
  data = {
    "AccountName": MIDDLEWARE_USERNAME_UYA,
    "Password": MIDDLEWARE_PASSWORD_UYA
  }

  response = requests.post(MIDDLEWARE_ENDPOINT_UYA + "Account/authenticate", json=data, verify=False)
  if response.status_code == 200:
    print("Authenticated API!")
    token = response.json()["Token"]
    headers[api] = { "Authorization": f"Bearer {token}" }
    return True
  else:
    print(response.status_code)
    print("ERROR AUTHENTICATING!")
    return None

def get_active_games(game_name_to_join):
  global headers
  if api not in headers:
    authenticate(api)
  
  route =  f"api/Game/list"
  response = requests.get(MIDDLEWARE_ENDPOINT_UYA + route, headers=headers[api], verify=False)

  if response.status_code == 200:
    games = response.json()
    for game in games:
      if game_name_to_join in game['GameName']:
        print("ID:", game['Id'], "GameId:", game['GameId'])
        return game['GameId']
  else:
    raise Exception(f"Got unknown error on get_active_games: {response.status_code}")
  
  raise Exception("Unknown game found.")

