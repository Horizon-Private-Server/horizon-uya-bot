import asyncio
import sys
import logging

from butils.utils import *
from connections.abstracttcp import AbstractTcp

from butils.gameinfo_parser import weaponParser, advancedRulesParser, mapParser, timeParser, gamerulesParser

class MasTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)

        self._logger = logging.getLogger('thug.mastcp')
        self._logger.setLevel(logging.DEBUG)

        self._logger.debug("Opening MAS...")
        self.loop.run_until_complete(self.start())

        self._logger.debug("Connection opened!")
        #self.loop.run_until_complete(asyncio.sleep(5))

        self._logger.debug("Starting Read routine ...")
        self.loop.create_task(self.read_data())
        self._logger.debug("Starting Write routine ...")
        self.loop.create_task(self.write_data())

        self.loop.run_until_complete(self.connect_tcp())

        self.loop.run_until_complete(self.begin_session())
        self.loop.run_until_complete(self.account_login())

        # self.loop.run_until_complete(self.connect_to_mls())

    # async def generate_access_key(self):
    #     self._logger.info("Generating access key ...")

    #     # Join game packet
    #     join_game_p1 = '0BC60001F331000000000000000000000000000000000000000000000000000000000000000000000000000000'
    #     join_game_p2 = '0000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    #     message = hex_to_bytes(join_game_p1 + bytes_to_hex(int_to_bytes_little(4, self._config['world_id'])) + join_game_p2)

    #     self.queue(message)

    #     while True:
    #         # Check the result
    #         data = self.dequeue()

    #         if data == None:
    #             await asyncio.sleep(.0001)
    #             continue

    #         if data[0] != 0x0A or data[1] != 0xBC:
    #             raise Exception('Unknown response!')

    #         elif data[0] == 0x0A and data[1] == 0xBC:
    #             self._access_key = data[174:]
    #             self._logger.info("Access key generated!")
    #             break

    async def connect_tcp(self):
        self._logger.info("Sending connect TCP ...")


        pkt = hex_to_bytes('1240006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE')
        self.queue(pkt)

        pkt = hex_to_bytes('0049000108010100BC290000E7D48669E1D5DD01BFD7B847A4BA6AB1E44EB12EDAD93485F274F3AC246C4FFAFAFF3E7AEC8AE4899CFF71F69AEACC16B8BE59CB9B88B55C8C719E41CBB18382')
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



    async def begin_session(self):
        self._logger.info("Beginning MAS session ...")
        pkt = hex_to_bytes('0B1E00010331000000000000000000000000000000000000000000000001000000')
        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            if len(data) != 53:
                self._logger.info(f"Got unexpected response! Expected len 53, got len {len(data)}! Data: {bytes_to_hex(data)}")

            beginsessionresponse = self.serialize_session_begin_response(data)

            self._session_key = beginsessionresponse['session_key']

            self._logger.info(f"Got session response! {beginsessionresponse}")
            break


    async def account_login(self):
        self._logger.info("Logging in ...")
        pkt = hex_to_bytes('0B6800010731001A00000000004DC81F00000000000000000000')

        # Session key
        pkt += hex_to_bytes(self._session_key)

        # Username
        pkt += str_to_bytes('CPU-001', 10)
        
        # UNK
        pkt += hex_to_bytes('C4D8240000000000EBFFFF7F08020000B0D82400FF00')

        # PASSWORD
        pkt += str_to_bytes('PASSWORD', 10)

        # UNK
        pkt += hex_to_bytes('000000000000000000000000000000002C2B15000000')

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            self._logger.info(f"Got Data: {bytes_to_hex(data)}")

            # 00006331514542485254723242534A425A4D000000
            raw = bytes_to_hex(data)
            data = deque([raw[i:i+2] for i in range(0,len(raw),2)])
            buf = ''.join([data.popleft() for _ in range(182)])

            self._mls_access_key = ''.join([data.popleft() for _ in range(16)])

            if self._mls_access_key == '00000000000000000000000000000000':
                raise Exception("Couldn't get MLS access key!")
        
            break
        # callback = ''.join([data.popleft() for _ in range(4)])
            # if callback != '00000000':
            #     sys.exit(1)

            # gameinfo['app_id'] = ''.join([data.popleft() for _ in range(4)])
            # gameinfo['min_players'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
            # gameinfo['max_players'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))
            # gameinfo['game_level'] = hex_to_int_little(''.join([data.popleft() for _ in range(4)]))

            # if len(data) != 53:
            #     self._logger.info(f"Got unexpected response! Expected len 53, got len {len(data)}! Data: {bytes_to_hex(data)}")

            # beginsessionresponse = self.serialize_session_begin_response(data)

            # self._logger.info(f"Got session response! {beginsessionresponse}")
            # break


    def get_access_key(self):
        self.loop.run_until_complete(self.generate_access_key())
        return self._access_key


    def serialize_session_begin_response(self, data):
        # \n2\x00
        # \x01\x041
        # \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00

        # \x00\x00\x00\x00
        # \x007\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        
        # \x00\x00\x00'
        raw = bytes_to_hex(data)
        data = deque([raw[i:i+2] for i in range(0,len(raw),2)])
        gameinfo = {}
        gameinfo['id'] = ''.join([data.popleft() for _ in range(6)])
        gameinfo['len'] = ''.join([data.popleft() for _ in range(2)])
        gameinfo['message_id'] = ''.join([data.popleft() for _ in range(21)])
        gameinfo['status'] = ''.join([data.popleft() for _ in range(4)])
        gameinfo['session_key'] = ''.join([data.popleft() for _ in range(17)])
        gameinfo['end'] = ''.join([data.popleft() for _ in range(3)])

        print(hex_to_bytes(gameinfo['session_key']))

        print(len(data))
        return gameinfo

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
