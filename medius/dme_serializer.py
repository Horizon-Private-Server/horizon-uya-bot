from utils.utils import *

from medius.dme_packets import *

RtSerializer = {
	b'\x00\x18' : {'name': 'player_connected', 'serializer': playerconnected.PlayerConnectedSerializer()},
	b'\x00\x10' : {'name': 'player_connected', 'serializer': playerconnected2.PlayerConnected2Serializer()},
}


def dme_serialize(data: bytes):
	data = bytearray(data)

	packets = []
	while data != b'':
		dme_id = bytes(data[0:2])
		packets.append(RtSerializer[dme_id]['serializer'].serialize(data))
	return packets
