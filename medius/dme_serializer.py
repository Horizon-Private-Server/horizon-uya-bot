from butils.utils import *

from medius.dme_packets import *

packets_both_tcp_and_udp = {'020E'}

TcpSerializer = {
	'0003': tcp_0003_broadcast_lobby_state.tcp_0003_broadcast_lobby_state,
	'0004': tcp_0004_tnw.tcp_0004_tnw,
	'000D': tcp_000D_game_started.tcp_000D_game_started,
	'000F': tcp_000F_playername_update.tcp_000F_playername_update,
	'0010': tcp_0010_initial_sync.tcp_0010_initial_sync,
	'0012': tcp_0012_player_left.tcp_0012_player_left,
	'0016': tcp_0016_player_connect_handshake.tcp_0016_player_connect_handshake,
	'0018': tcp_0018_initial_sync.tcp_0018_initial_sync,

	'0009': tcp_0009_set_timer.tcp_0009_set_timer,
	'0204': tcp_0204_player_killed.tcp_0204_player_killed,
	'0205': tcp_0205_unk.tcp_0205_unk,
	'0207': tcp_0207_defenses.tcp_0207_defenses,
	'020A': tcp_020A_player_respawned.tcp_020A_player_respawned,
	'020C': tcp_020C_info.tcp_020C_info,
	'020E': packet_020E_shot_fired.packet_020E_shot_fired,
	'0210': tcp_0210_player_joined.tcp_0210_player_joined,
	'0211': tcp_0211_player_lobby_state_change.tcp_0211_player_lobby_state_change,
	'0212': tcp_0212_host_headset.tcp_0212_host_headset,
	'0213': tcp_0213_player_headset.tcp_0213_player_headset,
}

UdpSerializer = {
	'0200': udp_0200_player_died.udp_0200_player_died,
	'0209': udp_0209_movement_update.udp_0209_movement_update,
	'020E': packet_020E_shot_fired.packet_020E_shot_fired,
	'020F': udp_020F_player_damage_animation.udp_020F_player_damage_animation,
	'0001': udp_0001_timer_update.udp_0001_timer_update,
}

def dmetcp_serialize(data: bytes):
	data = bytes_to_hex(data)
	data = deque([data[i:i+2] for i in range(0,len(data),2)])

	packets = []
	while len(data) != 0:
		dme_id = data.popleft() + data.popleft() # E.g. '0201'
		if dme_id in packets_both_tcp_and_udp: # Has both
			packets.append(TcpSerializer[dme_id].serialize('tcp', data))
		else:
			packets.append(TcpSerializer[dme_id].serialize(data))
	return packets

def dmeudp_serialize(data: bytes):
	data = bytes_to_hex(data)
	data = deque([data[i:i+2] for i in range(0,len(data),2)])

	packets = []
	while len(data) != 0:
		dme_id = data.popleft() + data.popleft() # E.g. '0201'
		if dme_id in packets_both_tcp_and_udp: # Has both
			packets.append(UdpSerializer[dme_id].serialize('udp', data))
		else:
			packets.append(UdpSerializer[dme_id].serialize(data))
	return packets
