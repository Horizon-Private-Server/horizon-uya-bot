from datetime import datetime
import logging
import asyncio

class TimeoutTimer():
    def __init__(self, loop, start_time, timeout):
        self._loop = loop
        self._start_time = start_time
        self._timeout = timeout
        self.alive = True

        self._timer_task = self._loop.create_task(self.timeout())

        self._logger = logging.getLogger('thug.timeout')
        self._logger.setLevel(logging.DEBUG)

    async def timeout(self):
        while self.alive:
            t = datetime.now()
            if ((t - self._start_time).total_seconds()) / 60 > self._timeout:
                self._logger.info("Timeout!")
                self._logger.info(f"Start time: {self._start_time} | End time: {t}")
                self._logger.info(f"Total time (min): {(t - self._start_time).total_seconds()/60}")
                self._logger.info(f"Total time (sec): {(t - self._start_time).total_seconds()}")
                self.alive = False
            await asyncio.sleep(10)

    async def kill(self):
        self._logger.info("Killing timer task...")
        self.alive = False
        await self._timer_task
        self._logger.info("Timer task killed.")