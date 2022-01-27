from utils.utils import *

from medius.rt import *

RtSerializer = {
	0x03 : {'name': 'CLIENT_APP_SINGLE', 'serializer': clientappsingle.ClientAppSingleSerializer()},
	0x1a : {'name': 'SERVER_CONNECT_COMPLETE', 'serializer': serverconnectcomplete.ServerConnectCompleteSerializer()},
}


def dme_serialize(data: bytes):
	data = bytearray(data)
	

#
# class Serializer:
# 	def serialize(self, packet: bytes):
# 		if packet[0] == 0x03:
#
#
#
# 	def _client_app_single(self, packet: bytes):
# 		arr = bytearray(packet)
# 		id = arr.pop(0)
# 		length = bytes_to_int_little(arr[0:2])
# 		arr.pop(0)
# 		arr.pop(0)
#
# 		source_player = arr.pop(0)
# 		buf = arr.pop(0)
#
# 		payload = arr
#
# 		serialized = {
# 			'name': 'client_app_single',
# 			'len': length,
# 			'src_player': source_player,
# 			'dme_packets': self._dme_serializer.serialize(bytes(arr))
# 		}
#
# 		return serialized
#
# 	def _connect_complete(self, packet: bytes):
# 		return {'name': 'connect_complete'}
#
# 	# =====================================
# 	# Packet Builders
# 	# =====================================
# 	def build_client_app_single(self, data: bytes):
# 		id = b'\x03'
# 		length = int_to_bytes_little(2, len(data))
# 		return id+length+data
