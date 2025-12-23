import asyncio
import time

import aiohttp


class VkApi:
    """
    Отправляет запросы по VK API и контролирует кол-во запросов в секунду.
    """

    def __init__(self, token: str, proxy: str = None, v: str = '5.199', is_group_token: bool = False):
        self.token = token
        self.proxy = proxy
        self.v = v

        self.RPS_DELAY = (1 / 20) if is_group_token else (1 / 3)
        self.last_request_dt = time.time()

        self.session = aiohttp.ClientSession()

    async def _delay(self):
        delay_time = max(self.RPS_DELAY - (time.time() - self.last_request_dt), 0)
        if delay_time:
            await asyncio.sleep(delay_time)

    async def method(self, method: str, params: dict):
        await self._delay()
        url = "https://api.vk.com/method/" + method
        params['access_token'] = self.token
        params['v'] = self.v
        async with self.session.post(url, params=params, proxy=self.proxy) as response:
            return await response.json()

    async def send(self, url: str, params: dict, wait: int = 25):
        async with self.session.get(url, params=params, proxy=self.proxy, timeout=wait + 10) as response:
            response = await response.json()
        return response

    async def close(self):
        await self.session.close()
