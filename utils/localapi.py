from aiohttp import web
from medius.dme_packets import *


class LocalApi():
    def __init__(self, loop, model, account_id):
        self._loop = loop
        self._model = model
        self._port = account_id + 10000

        loop.run_until_complete(self.start())

    async def packet(self, request):
        data = await request.post()
        packet = data.get('packet')
        packets = packet.split("\n")
        packets = [packet.strip() for packet in packets if packet.strip()]

        for packet in packets:
            print(f"Injecting packet: {packet}")
            exec(packet)

        return web.json_response({'message': f'Success'})


    async def start(self):
        app = web.Application()
        app.router.add_post('/packet', self.packet)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self._port)

        await site.start()
        port_select = site._server.sockets[0].getsockname()[1]
