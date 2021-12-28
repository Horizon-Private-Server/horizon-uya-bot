import asyncio
import sys
import logging

from utils import *
from connections.abstracttcp import AbstractTcp

from serializer import serializer


class DmeTcp(AbstractTcp):
    def __init__(self, loop, config, ip: str, port: int):
        super().__init__(loop, config, ip, port)
        self._logger = logging.getLogger('thug.dmetcp')
        self._logger.setLevel(logging.DEBUG)


        self._player_id = None
        self._player_count = 0

        self.loop.run_until_complete(self.start())
        self.loop.create_task(self.read())
        self.loop.create_task(self.write())
        self.loop.create_task(self.echo())


    async def main(self):
        while True:

            if self.qsize() != 0:
                packet = self.dequeue()
                serialized = serializer.serialize(packet)
                self.process(serialized)
            await asyncio.sleep(self._wait_time_for_packets)

    def process(self, serialized: dict):
        if serialized['name'] == 'client_app_single':
            self.process_client_app_single(serialized)



    def process_client_app_single(self, serialized: dict):
        self._logger.info(serialized)

        hex_str = bytes_to_hex(serialized['payload'])
        if "F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE0016" in hex_str:
            # Initial connect packet
            self._respond_to_initial_connect_ping(serialized['src_player'])

        elif serialized['len'] == 474 and serialized['payload'][57:72] == b'tNW_GameSetting':
            # TODO: RESPOND TO TNW GAMESETTING
            new_pkt = hex_to_bytes('0314000000001604010300000000000000000000000000024C00000F0100000000000000000003000300000000001A0000005465737400000000000000000300000F0100000000000000001003000300000000001A00000054657374000000000000000000000D02000201031A000000001604010300000000000200000000000000021300000000')
            self.queue(new_pkt)

    async def connect_to_dme_world_stage_1(self, access_key):
        # Initial connect to DME TCP
        self._logger.info("Connecting to dme world Stage [1] ...")
        pkt = hex_to_bytes('156B00010801')
        pkt += int_to_bytes_little(2, self._config['world_id'])
        pkt += hex_to_bytes('BC29000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        pkt += self._config['session_key'].encode()
        pkt += access_key

        self.queue(pkt)

        # wait half a second
        await asyncio.sleep(self._wait_time_for_packets)

        # Check the result
        data = self.dequeue()
        if data[0] != 0x07:
            raise Exception('Unknown response!')
        self._player_id = bytes_to_int_little(data[6:8])
        self._player_count = bytes_to_int_little(data[8:10])

        data = self.dequeue()
        if data[0] != 0x18: # we can ignore this
            raise Exception('Unknown response!')

        self._logger.info(f"Connected Stage [1]! Player ID: {self._player_id} | Player count: {self._player_count}")

    async def connect_to_dme_world_stage_2(self):
        self._logger.info("Connecting to dme world Stage [2] ...")
        pkt = hex_to_bytes('170000')

        self.queue(pkt)
        self._logger.info("Connected Stage [2]!")


    def get_player_id(self):
        return self._player_id

    def get_player_count(self):
        return self._player_count

    def _respond_to_initial_connect_ping(self, src_player: int):
        '''
        00 -- player destination id

        00001802000000 -- unk1
        01 -- source player id
        000000C00002641418000000000000 -- unk2
        E038 -- unk_gen
        000001000000001002 - unk3
        01 -- source player id
        C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE0016 -- unk4
        03 -- unk5
        01 -- source player id
        0300000000000000000000000000 unk6
        '''
        dst_id = int_to_bytes_little(1, src_player)
        unk1 = hex_to_bytes('00001802000000')
        src_id = int_to_bytes_little(1, self._player_id)
        unk2 = hex_to_bytes('000000C00002641418000000000000')
        unk_gen = hex_to_bytes('E038')
        unk3 = hex_to_bytes('000001000000001002')
        unk4 = hex_to_bytes('C0A8010200006B8F99EC1BAF06D2674284B5305EE6E38B1DE7331F2FBF31DE497228B7C52162F18DAE8913C40C43C0E890D14EEE16AD07C64FD9281D8B972D78BE78D1B290CE0016')
        unk5 = hex_to_bytes('03')
        unk6 = hex_to_bytes('0300000000000000000000000000')


        payload = dst_id + unk1 + src_id + unk2 + unk_gen + unk3 + src_id + unk4 + unk5 + src_id + unk6
        packet = serializer.build_client_app_single(payload)
        self.queue(packet)