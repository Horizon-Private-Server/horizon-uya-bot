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
        self._logger.setLevel(logging.WARNING)

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

        self._alive = False


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
                raise Exception('Unknown')
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

            if beginsessionresponse['status'] != '00000000':
                raise Exception('Got invalid status code!')


            self._session_key = beginsessionresponse['session_key']

            self._logger.info(f"Got session response! {beginsessionresponse}")
            break


    async def account_login(self):
        self._logger.info("Logging in ...")
        pkt = hex_to_bytes('0B6800010731001A00000000004DC81F00000000000000000000')

        # Session key
        pkt += self._session_key

        # Username
        pkt += str_to_bytes(self._config['username'], 10)
        
        # UNK
        pkt += hex_to_bytes('C4D8240000000000EBFFFF7F08020000B0D82400FF00')

        # PASSWORD
        pkt += str_to_bytes(self._config['password'], 10)

        # UNK
        pkt += hex_to_bytes('000000000000000000000000000000002C2B15000000')

        self.queue(pkt)

        while True:
            # Check the result
            data = self.dequeue()

            if data == None:
                await asyncio.sleep(.0001)
                continue

            raw = bytes_to_hex(data)
            data = deque([raw[i:i+2] for i in range(0,len(raw),2)])
            buf = ''.join([data.popleft() for _ in range(182)])

            self._access_key = hex_to_bytes(''.join([data.popleft() for _ in range(16)]))

            if self._access_key == '00000000000000000000000000000000':
                raise Exception("Couldn't get MLS access key!")
        
            self._logger.info("Login success!")

            break


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
        gameinfo['session_key'] = hex_to_bytes(''.join([data.popleft() for _ in range(17)]))
        gameinfo['end'] = ''.join([data.popleft() for _ in range(3)])

        print(len(data))
        return gameinfo
