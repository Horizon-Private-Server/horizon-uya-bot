import asyncio
import sys
import logging

from butils.utils import *
from connections.abstracttcp import AbstractTcp

from butils.gameinfo_parser import weaponParser, advancedRulesParser, mapParser, timeParser, gamerulesParser
from constants.constants import VALID_GAME_MODES

class MlsTcp(AbstractTcp):
    def __init__(self, loop, mls_log_level, ip: str, port: int, session_key, access_key):
        super().__init__(loop, ip, port)

        self.access_key = access_key
        self.session_key = session_key

        self.gameinfo = None

        self.dme_session_key = None
        self.dme_access_key = None
        self.dme_ip = None
        self.dme_port = None

        self._logger = logging.getLogger('thug.mlstcp')
        self._logger.setLevel(mls_log_level)

        self.loop.run_until_complete(self.start())
        
        
    async def connect(self, world_id):
        await asyncio.wait_for(self.connect_to_mls(), timeout=7.0)
        await asyncio.wait_for(self.get_game_info(world_id), timeout=5.0)
        await asyncio.wait_for(self.join_game(world_id), timeout=5.0)

        self.loop.create_task(self.check_game_info_alive(world_id))


    async def connect_to_mls(self):
        # Need to let server process access token
        await asyncio.sleep(2)
        self._logger.info("Connecting to MLS ...")

        pkt = hex_to_bytes('1240006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE')
        self.queue(pkt)

        #pkt = hex_to_bytes('006B000108010000BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt = hex_to_bytes('006A000108010100BC290000E7D48669E1D5DD01BFD7B847A4BA6AB1E44EB12EDAD93485F274F3AC246C4FFAFAFF3E7AEC8AE4899CFF71F69AEACC16B8BE59CB9B88B55C8C719E41CBB18382')

        pkt += self.session_key
        pkt += self.access_key

        self.queue(pkt)

        while True:
                # Check the result
                data = self.dequeue()

                if data == None:
                    await asyncio.sleep(.0001)
                    continue

                if bytes_to_hex(data)[0:2] != '13':
                    raise Exception()
                break

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if bytes_to_hex(data)[0:2] != '14':
                raise Exception()
            break

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if bytes_to_hex(data)[0:2] != '07':
                raise Exception()
            break

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if bytes_to_hex(data)[0:2] != '1A':
                raise Exception()
            break

        self._logger.info("Connected to MLS!")


    async def get_game_info(self, world_id):
        self._logger.info("Getting Game Info ...")
        pkt = hex_to_bytes('0B2E00013331000000000000000000000000000000C01D480000')
        pkt += self.session_key
        pkt += hex_to_bytes("0000")
        pkt += int_to_bytes_little(4, world_id)

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            self.gameinfo = self.serialize_game_info(data)
            break

    async def check_game_info_alive(self, world_id):
        await asyncio.sleep(15)
        while self.alive:
            await asyncio.sleep(30)
            self.clear_queue()
            self._logger.debug("Checking if game info is valid ...")
            pkt = hex_to_bytes('0B2E00013331000000000000000000000000000000C01D480000')
            pkt += self.session_key
            pkt += hex_to_bytes("0000")
            pkt += int_to_bytes_little(4, world_id)

            self.queue(pkt)

            while True:
                # Check the result
                data = self.dequeue()

                if data == None:
                    await asyncio.sleep(.0001)
                    continue
                try:
                    self.serialize_game_info(data, check_game_settings=False)
                except Exception as e:
                    self._logger.info("Game info no longer valid! Exiting!")
                    self.alive = False
                    return
                break

    def serialize_game_info(self, raw_gameinfo0, check_game_settings=True):
        gameinfo = {}
        raw_gameinfo0 = bytes_to_hex(raw_gameinfo0)
        #self._logger.info(raw_gameinfo0)

        data = deque([raw_gameinfo0[i:i+2] for i in range(0,len(raw_gameinfo0),2)])
        buf = ''.join([data.popleft() for _ in range(29)])

        callback = ''.join([data.popleft() for _ in range(4)])
        if callback != '00000000':
            self._logger.debug(callback)
            self._logger.debug("Game Info Returned Error!")
            raise Exception(f"Game Info Returned Error(callback: {callback})")

        gameinfo['app_id'] = ''.join([data.popleft() for _ in range(4)])
        gameinfo['min_players'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['max_players'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['game_level'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['player_skill_level'] = hex_to_int_little(''.join([data.popleft() for _ in range(3)])); data.popleft()
        gameinfo['player_count'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        stats = ''.join([data.popleft() for _ in range(256)])
        gameinfo['game_name'] = ''.join([data.popleft() for _ in range(64)])
        gameinfo['rules_set'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['generic_field_1'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['generic_field_2'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['generic_field_3'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['game_status'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        gameinfo['game_host_type'] = ''.join([data.popleft() for _ in range(4)])
        if check_game_settings and (gameinfo['game_status'] != 1 or gameinfo['player_count'] == 8):
            self._logger.info(f"Invalid game settings: {gameinfo}")
            raise Exception(f"Invalid game settings: {gameinfo}")

        game = {'game_name': gameinfo['game_name']}
        game['weapons'] = weaponParser(gameinfo['player_skill_level'])
        game['advanced_rules'] = advancedRulesParser(gameinfo['generic_field_3'])
        game['map'] = mapParser(gameinfo['generic_field_3'])
        game['game_length'] = timeParser(gameinfo['generic_field_3'])
        game_mode, submode = gamerulesParser(gameinfo['generic_field_3'])
        game['game_mode'] = game_mode
        game['submode'] = submode

        game['frag'] = None
        game['cap_limit'] = None
        
        if game['game_length'] == 'no_time_limit':
            game['game_length'] = None
        else:
            game['game_length'] = int(game['game_length'].split("_")[0])

        binary = bin(gameinfo['generic_field_3'])[2:]
        length = len(binary)
        leftover = 32 - length
        binary_full = leftover * '0' + binary
        game['cap_limit'] = int(binary_full[5:9], 2)
        game['frag'] = int(binary_full[10:13], 2) * 5
        if game['frag'] == 0:
            game['frag'] = None

        if game['map'] not in VALID_GAME_MODES.keys():
            raise Exception(f'Map {game["map"]} not in valid map settings!')
        if game['game_mode'] not in VALID_GAME_MODES[game['map']]:
            raise Exception(f'Game mode ({game["game_mode"]}) not supported for {game["map"]}')

        return game

    async def join_game(self, world_id):
        self._logger.info("Joining Game ...")
        pkt = hex_to_bytes('0BC60001F3310000000000000000000000000000000000000000')
        pkt += self.session_key
        pkt += hex_to_bytes("0000")
        pkt += int_to_bytes_little(4, world_id)
        pkt += hex_to_bytes("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            self.serialize_join_game(data)
            break

    def clear_queue(self):
        while self.dequeue() != None:
            continue

    def serialize_join_game(self, raw_joingame):
        raw_joingame = bytes_to_hex(raw_joingame)
        data = deque([raw_joingame[i:i+2] for i in range(0,len(raw_joingame),2)])
        buf = ''.join([data.popleft() for _ in range(45)])

        self.dme_ip = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        self.dme_port = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        buf = ''.join([data.popleft() for _ in range(92)])

        self.dme_session_key = hex_to_bytes(''.join([data.popleft() for _ in range(17)]))
        self.dme_access_key = hex_to_bytes(''.join([data.popleft() for _ in range(16)]))

