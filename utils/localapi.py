from aiohttp import web


port = 10000

class LocalApi():
    def __init__(self, loop, model):
        self._loop = loop
        self._model = model

        loop.run_until_complete(self.start())

    async def packet(self, request):
        data = await request.post()
        name = data.get('name')
        age = data.get('age')

        if name and age:
            print(name, age)
        else:
            print("Invalid post to server")


    async def start(self):
        app = web.Application()
        app.router.add_post('/packet', self.packet)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)

        await site.start()
        port_select = site._server.sockets[0].getsockname()[1]
