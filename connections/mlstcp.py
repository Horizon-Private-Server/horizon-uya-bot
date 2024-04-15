import asyncio
import sys
import logging

from butils.utils import *
from connections.abstracttcp import AbstractTcp

from butils.gameinfo_parser import weaponParser, advancedRulesParser, mapParser, timeParser, gamerulesParser

class MlsTcp(AbstractTcp):
    def __init__(self, loop, ip: str, port: int, session_key, access_key):
        super().__init__(loop, ip, port)

        self.access_key = access_key
        self.session_key = session_key

        self.gameinfo = None

        self.dme_session_key = None
        self.dme_access_key = None
        self.dme_ip = None
        self.dme_port = None

        self._logger = logging.getLogger('thug.mlstcp')
        self._logger.setLevel(logging.DEBUG)

        self.loop.run_until_complete(self.start())
        
        



    async def connect_to_mls(self):
        await asyncio.wait_for(self._connect_to_mls(), timeout=5.0)

    async def _connect_to_mls(self):
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
        await asyncio.wait_for(self._get_game_info(world_id), timeout=5.0)

    async def _get_game_info(self, world_id):
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

            self.serialize_game_info(data)
            break

    def serialize_game_info(self, raw_gameinfo0):
        gameinfo = {}
        raw_gameinfo0 = bytes_to_hex(raw_gameinfo0)
        data = deque([raw_gameinfo0[i:i+2] for i in range(0,len(raw_gameinfo0),2)])
        buf = ''.join([data.popleft() for _ in range(29)])

        callback = ''.join([data.popleft() for _ in range(4)])
        if callback != '00000000':
            self._logger.debug(callback)
            self._logger.debug("Game Info Returned Error!")
            sys.exit(1)

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
        if gameinfo['game_status'] != 1 or gameinfo['player_count'] == 8:
            self._logger.info("Invalid game settings.")
            sys.exit(1)

        game = {'game_name': gameinfo['game_name']}
        game['weapons'] = weaponParser(gameinfo['player_skill_level'])
        game['advanced_rules'] = advancedRulesParser(gameinfo['generic_field_3'])
        game['map'] = mapParser(gameinfo['generic_field_3'])
        game['game_length'] = timeParser(gameinfo['generic_field_3'])
        game_mode, submode = gamerulesParser(gameinfo['generic_field_3'])
        game['game_mode'] = game_mode
        game['submode'] = submode

        self.gameinfo = game

    async def join_game(self, world_id):
        await asyncio.wait_for(self._join_game(world_id), timeout=5.0)

    async def _join_game(self, world_id):
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


    def serialize_join_game(self, raw_joingame):
        raw_joingame = bytes_to_hex(raw_joingame)
        data = deque([raw_joingame[i:i+2] for i in range(0,len(raw_joingame),2)])
        buf = ''.join([data.popleft() for _ in range(45)])

        self.dme_ip = hex_to_str(''.join([data.popleft() for _ in range(16)]))
        self.dme_port = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
        buf = ''.join([data.popleft() for _ in range(92)])

        self.dme_session_key = hex_to_bytes(''.join([data.popleft() for _ in range(17)]))
        self.dme_access_key = hex_to_bytes(''.join([data.popleft() for _ in range(16)]))

        self._logger.info(self._config)

