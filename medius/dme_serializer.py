from utils.utils import *

from medius.dme_packets import *

RtSerializer = {
	b'\x00\x04' : {'name': 'tnw_gamesettings', 'serializer': tnwgamesettings.tnwGameSettingsSerializer()},
	b'\x00\x10' : {'name': 'tcp_0010_initial_sync', 'serializer': tcp_0010_initial_sync.tcp_0010_initial_sync()},
	b'\x00\x16' : {'name': 'tcp_0016_player_connect_handshake', 'serializer': tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake()},
	b'\x00\x18' : {'name': 'tcp_0018_initial_sync', 'serializer': tcp_0018_initial_sync.tcp_0018_initial_sync()},
	b'\x00\x09' : {'name': 'tcp_0009_unk', 'serializer': tcp_0009_unk.tcp_0009_unk()},
	b'\x02\x12' : {'name': 'tcp_0212_host_headset', 'serializer': tcp_0212_host_headset.tcp_0212_host_headset()},
	b'\x00\x0F' : {'name': 'playerupdate', 'serializer': playerupdate.PlayerUpdateSerializer()},

}


def dme_serialize(data: bytes):
	data = bytearray(data)

	packets = []
	while data != b'':
		dme_id = bytes(data[0:2])
		packets.append(RtSerializer[dme_id]['serializer'].serialize(data))
	return packets
