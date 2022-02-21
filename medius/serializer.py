from utils.utils import *

from medius.rt import *

TcpSerializer = {
	0x03 : {'name': 'CLIENT_APP_SINGLE', 'serializer': clientappsingle.ClientAppSingleSerializer('tcp')},
	0x1a : {'name': 'SERVER_CONNECT_COMPLETE', 'serializer': serverconnectcomplete.ServerConnectCompleteSerializer()},
}

UdpSerializer = {
	0x03 : {'name': 'CLIENT_APP_SINGLE', 'serializer': clientappsingle.ClientAppSingleSerializer('udp')},
	0x1a : {'name': 'SERVER_CONNECT_COMPLETE', 'serializer': serverconnectcomplete.ServerConnectCompleteSerializer()},
}
