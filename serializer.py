
from utils import *


class SerializerMap:
	def __init__(self):
		

		self._map = {
			0x03: self._client_app_single,
			0x1a: self._connect_complete
		}

	# =====================================
	# Serializers
	# =====================================

	def serialize(self, packet: bytes):
		return self._map[packet[0]](packet)

	def _client_app_single(self, packet: bytes):
		arr = bytearray(packet)
		id = arr.pop(0)
		length = bytes_to_int_little(arr[0:2])
		arr.pop(0)
		arr.pop(0)

		source_player = arr.pop(0)

		payload = arr

		return {'name': 'client_app_single', 'len': length, 'src_player': source_player, 'payload': payload}

	def _connect_complete(self, packet: bytes):
		return {'name': 'connect_complete'}

	# =====================================
	# Packet Builders
	# =====================================

	def build_client_app_single(self, data: bytes):
		id = b'\x03'
		length = int_to_bytes_little(2, len(data))
		return id+length+data


serializer = SerializerMap()