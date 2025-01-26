import os
import logging
from logging.handlers import RotatingFileHandler
import asyncio
import json
from collections import deque
from datetime import datetime, timedelta
from copy import deepcopy
import sys
import ssl
import functools

import websockets
import requests
import aiohttp

from live.livetrackerbackend import LiveTrackerBackend
from live.schemas import *
from live.uya_game import *

logger = logging.getLogger("live")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Rotating file handler to log to a file
if os.getenv("LIVE_SOCKET_SIMULATED") == "True":
    log = 'logs_sim/live.log'
    os.makedirs("logs_sim", exist_ok=True)  # Create the directory if it doesn't exist
else:
    log = 'logs/live.log'
    os.makedirs("logs", exist_ok=True)  # Create the directory if it doesn't exist

file_handler = RotatingFileHandler(
    log,       # Log file name
    maxBytes=5*1024*1024,  # Max file size (e.g., 5 MB)
    backupCount=10          # Keep up to 5 backup log files
)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(name)s | %(levelname)s | %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def authenticate(protocol: str, host: str, username: str, password: str) -> str:
    """
    Makes an authentication POST request to the Horizon Middleware server to
    exchange a username and password for a JWT Bearer Token.

    :param protocol: "HTTP" or "HTTPS".
    :param host: Host name and optional port of the target Horizon Middleware server
        (i.e., "stats.rac-horizon.com" or "111.222.111.222:1234").
    :param username: Username to authenticate.
    :param password: Password for username.
    :return: The raw JWT Bearer Token.
    """
    logger.debug(f"authenticate: Authenticating token ...")
    authentication_url: str = f"{protocol}://{host}/Account/authenticate"

    authentication_body: dict[str, str] = {
        "AccountName": username,
        "Password": password
    }

    auth_response = requests.post(
        authentication_url,
        json=authentication_body,
        verify=protocol != "https"
    )

    auth_response_json: dict[str, any] = json.loads(auth_response.text)

    return auth_response_json["Token"]

def retry_async(retries=3, delay=2, exception_types=(Exception,)):
    """
    A decorator to automatically retry a function in case of specified exceptions.

    :param retries: Number of retry attempts.
    :param delay: Delay between retries in seconds.
    :param exception_types: Tuple of exception types to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exception_types as e:
                    attempt += 1
                    logger.warning(f"Function '{func.__name__}' failed on attempt {attempt}/{retries}: {str(e)}")
                    if attempt < retries:
                        await asyncio.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator

@retry_async(retries=3, delay=2)
async def get_players_online(protocol: str, host: str, token: str) -> list[dict[str, any]]:
    """
    Makes a request to the Horizon Middleware account API which returns
    all players online.

    :param protocol: "HTTP" or "HTTPS".
    :param host: Host name and optional port of the target Horizon Middleware server
        (i.e., "stats.rac-horizon.com" or "111.222.111.222:1234").
    :param token: The requesting user's authentication token.
    :return:
    """
    headers = {"Authorization": f"Bearer {token}"}
    active_games_url = f"{protocol}://{host}/Account/getOnlineAccounts/"
    async with aiohttp.ClientSession() as session:
        async with session.get(active_games_url, headers=headers, ssl=False) as response:
            if response.status == 200:  # Check if response status code is 200 (OK)
                return await response.json()  # Parse the response as JSON if status is OK
            
            logger.warning(f"get_players_online got {response.status} from {protocol}://{host}")
            return []

@retry_async(retries=3, delay=2)
async def get_active_games(protocol: str, host: str, token: str) -> list[dict[str, any]]:
    """
    Makes a request to the Horizon Middleware account API which returns
    the active games.

    :param protocol: "HTTP" or "HTTPS".
    :param host: Host name and optional port of the target Horizon Middleware server
        (i.e., "stats.rac-horizon.com" or "111.222.111.222:1234").
    :param token: The requesting user's authentication token.
    :return:
    """
    headers = {"Authorization": f"Bearer {token}"}
    active_games_url = f"{protocol}://{host}/api/Game/list"
    async with aiohttp.ClientSession() as session:
        async with session.get(active_games_url, headers=headers, ssl=False) as response:
            if response.status == 200:  # Check if response status code is 200 (OK)
                return await response.json()  # Parse the response as JSON if status is OK

            logger.warning(f"get_active_games got {response.status} from {protocol}://{host}")
            return []


class UyaLiveTracker():
    def __init__(self, loop, prod_ip, protocol, host, horizon_username, horizon_password, port:int=8888, read_tick_rate:int=10, write_tick_rate:int=10, read_games_api_rate:int=10, write_delay:int=30):
        self._simulated = os.getenv("LIVE_SOCKET_SIMULATED") == "True"
        self._prod_server_ip = prod_ip
        self._ip = '0.0.0.0'
        self._port = port if not self._simulated else port - 1
        self._loop = loop

        self._backend = LiveTrackerBackend(server_ip=self._prod_server_ip, simulated=self._simulated, log_level='INFO')

        # In seconds
        self._read_games_api_rate = read_games_api_rate

        # Ticks per second
        self._read_tick_rate = 1 / read_tick_rate
        self._write_tick_rate = 1 / write_tick_rate
        self._world_state = []
        self._world_state_history = deque() # For automatic popping so we don't need to remove.
        self._games = dict()

        # Delay in seconds for writing to the websocket to prevent cheating
        self._write_delay = write_delay

        with open("live/uya_live_map_boundaries.json", "r") as f:
            self._transform_coord_map = json.loads(f.read())

        self._players_online_poll_interval = 60
        self._token_poll_interval = 3600
        self._players_online = []
        self._games_online = []

        self._protocol = protocol
        self._host = host
        self._horizon_username = horizon_username
        self._horizon_password = horizon_password
        self._token: str = authenticate(
            protocol=self._protocol,
            host=self._host,
            username=self._horizon_username,
            password=self._horizon_password
        )

    async def start(self):
        self._backend.start(self._loop)
        self._loop.create_task(self.read_prod_socket())
        self._loop.create_task(self.read_games_api())
        self._loop.create_task(self.poll_active_online())

    async def on_websocket_connection(self, websocket, path):
        logger.info(f"Websocket incoming connection: {websocket.remote_address}")
        # Register.
        self._connected.add(websocket)
        websocket.connected = True
        try:
            while websocket.connected:
                await asyncio.sleep(.001)
        # except Exception:
        #     self._logger.exception("message2")
        finally:
            logger.info("Websocket disconnected!")
            # Unregister.
            self._connected.remove(websocket)

    async def poll_active_online(self) -> None:
        # Poll forever and update internal variable
        while True:
            # Try except so that if the db goes down, it will work when the db comes back online
            try:
                logger.debug("Polling active players/games online ...")
                self._players_online: list[dict] = await get_players_online(self._protocol, self._host, self._token)
                self._games_online: list[dict] = await get_active_games(self._protocol, self._host, self._token)
            except Exception as e:
                logger.error("[uya] poll_active_online failed to update!", exc_info=True)

            await asyncio.sleep(self._players_online_poll_interval)

    def dump(self):
        current_time = datetime.now()
        delay_threshold = current_time - timedelta(seconds=self._write_delay)
        
        worlds = []
        while self._world_state_history and self._world_state_history[0][0] < delay_threshold:
            self._world_state_history.popleft()  # Remove the element from the front if it meets the condition

        if self._world_state_history:
            worlds = self._world_state_history[0][1]

        data = json.dumps([world_state.dict() for world_state in worlds])
        return data

    async def read_prod_socket(self):
        while True:
            try:
                worlds:list[dict] = self._backend.get_world_states()
                worlds = [UYALiveGameSession(**world) for world in worlds]
                self._world_state = []

                for world in worlds:                    
                    if not self._simulated and world.world_id not in self._games.keys():
                        continue

                    if not self._simulated and world.map == 'UNKNOWN': # We didn't get anything from the socket. Use the games api instead
                        game = self._games[world.world_id]
                        world.map = game.map
                        world.name = game.name
                        world.game_mode = game.game_mode

                    world_players = list(sorted(world.players, key=lambda player: player.player_id))
                    for idx in range(len(world_players)):
                        world_players[idx].coord = self.transform_coord(world.map, world_players[idx].coord)
                    world.players = world_players

                    self._world_state.append(world)

                self._world_state_history.append((datetime.now(), deepcopy(self._world_state)))

            except Exception as e:
                logger.error("read_prod_socket failed to update!", exc_info=True)

            await asyncio.sleep(self._read_tick_rate)

    async def read_games_api(self):
        while True:
            try:
                games = self.get_games()
                self._games = {game.id-1: game for game in games}
            except Exception as e:
                logger.error("read_games_api failed to update!", exc_info=True)
            await asyncio.sleep(self._read_games_api_rate)

    def get_games(self) -> list[UyaGameOnlineSchema]:
        games = []

        # Process each game
        for game in self._games_online:
            game_metadata = json.loads(game["Metadata"]) if "Metadata" in game.keys() and game["Metadata"] else {}
            game_players = list(filter(lambda _player: _player["GameId"] is not None and _player["GameId"] == game["GameId"], self._players_online))

            if "CustomMap" in game_metadata.keys() and game_metadata["CustomMap"] != None:
                map = game_metadata["CustomMap"]
            else:
                map = uya_map_parser(game["GenericField3"], game_metadata)

            game_mode, game_type = uya_gamemode_parser(game["GenericField3"])

            timelimit = uya_time_parser(game["GenericField3"])

            games.append(UyaGameOnlineSchema(
                id=int(game["GameId"]),
                name=game["GameName"][0:15].strip(),
                game_status=game["WorldStatus"],
                map=map,
                time_started=game["GameStartDt"][:26] if game["WorldStatus"] == "WorldActive" and game["GameStartDt"] is not None else "Not yet started",
                time_limit=timelimit,
                game_mode=game_mode,
                game_type=game_type,
                last_updated=str(datetime.now()),
                players=[UyaPlayerOnlineSchema(username=player["AccountName"]) for player in game_players]
            ))

        return deepcopy(games)

    def transform_coord(self, map:str, coord:tuple):
        if map not in self._transform_coord_map.keys():
            return [50,50,50]

        min_maxes:dict = self._transform_coord_map[map]
        new_coord = list(coord)
        new_coord[0] = ((coord[0] - min_maxes["xmin"]) / (min_maxes["xmax"] - min_maxes["xmin"])) * 100
        new_coord[1] = 100 - ((coord[1] - min_maxes["ymin"]) / (min_maxes["ymax"] - min_maxes["ymin"])) * 100

        return tuple(new_coord)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tracker = UyaLiveTracker(loop, os.getenv("LIVE_READ_PROD_SOCKET_IP"), os.getenv("LIVE_MIDDLEWARE_PROTOCOL"), os.getenv("LIVE_MIDDLEWARE_HOST"), os.getenv("LIVE_MIDDLEWARE_USERNAME"), os.getenv("LIVE_MIDDLEWARE_PASSWORD"))
    loop.run_until_complete(tracker.start())
    while True:
        loop.run_until_complete(asyncio.sleep(2))
        print(datetime.now(), tracker.dump())