import asyncio
import sys
import logging

from butils.utils import *
from connections.abstracttcp import AbstractTcp

from butils.gameinfo_parser import weaponParser, advancedRulesParser, mapParser, timeParser, gamerulesParser

class MlsTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)

        self._config['session_key'] += '\x00'
        self._access_key = None

        self._logger = logging.getLogger('thug.mlstcp')
        self._logger.setLevel(logging.DEBUG)

        self._logger.debug("Opening connection 1...")
        self.loop.run_until_complete(self.start())

        self._logger.debug("Connection opened!")
        #self.loop.run_until_complete(asyncio.sleep(5))

        self._logger.debug("Starting Read routine ...")
        self.loop.create_task(self.read_data())
        self._logger.debug("Starting Write routine ...")
        self.loop.create_task(self.write_data())
        self.loop.run_until_complete(self.generate_access_key())
        self.loop.run_until_complete(self.get_game_info())


        # TODO: add CTF/Siege modes
        # if self._config['gameinfo']['game_mode'] != 'Deathmatch' or self._config['gameinfo']['submode'] != 'Teams':
        #     self._logger.warning("Incorrect game mode")
        #     sys.exit(1)

        self.loop.create_task(self.echo())
        self.loop.run_until_complete(self.connect_to_mls())

    async def generate_access_key(self):
        self._logger.info("Generating access key ...")

        # Join game packet
        join_game_p1 = '0BC60001F331000000000000000000000000000000000000000000000000000000000000000000000000000000'
        join_game_p2 = '0000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        message = hex_to_bytes(join_game_p1 + bytes_to_hex(int_to_bytes_little(4, self._config['world_id'])) + join_game_p2)

        self.queue(message)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x0A or data[1] != 0xBC:
                raise Exception('Unknown response!')

            elif data[0] == 0x0A and data[1] == 0xBC:
                self._access_key = data[174:]
                self._logger.info("Access key generated!")
                break

    async def connect_to_mls(self):
        self._logger.info("Connecting to MLS ...")
        pkt = hex_to_bytes('006B000108010000BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += self._access_key

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if data[0] != 0x07:
                raise Exception('Unknown response!')

            elif data[0] == 0x07:
                break

        while True:
            # Check the result
            data = self.dequeue()

            if data[0] != 0x1A:
                raise Exception('Unknown response!')

            elif data[0] == 0x1A:
                break
        self._logger.info("Connected!")

    def get_access_key(self):
        self.loop.run_until_complete(self.generate_access_key())
        return self._access_key


    async def get_game_info(self):
        self._logger.debug("Getting Game Info ...")
        pkt = hex_to_bytes('0B2E00013331000000000000000000000000000000C01D480000')
        pkt += self._config['session_key'].encode()
        pkt += hex_to_bytes("0000")
        pkt += int_to_bytes_little(4, self._config['world_id'])

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

        self._config['gameinfo'] = game
