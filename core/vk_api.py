import asyncio
import logging
import ssl
import time

import aiohttp
import certifi.core

from core.limits import VkLimits


class VkApi:
    """
    Отправляет запросы по VK API и контролирует кол-во запросов в секунду.
    """

    def __init__(self, token: str, proxy: str = None, v: str = '5.199', is_group_token: bool = False):
        self.token = token
        self.proxy = proxy
        self.v = v
        self.cert = ssl.create_default_context(cafile=certifi.core.where())

        self.RPS_DELAY = VkLimits.GROUP_MESSAGE_LIMIT if is_group_token else VkLimits.USER_MESSAGE_LIMIT
        self.last_request_dt = time.time()

        self.session = aiohttp.ClientSession()

    async def _delay(self):
        delay_time = max(self.RPS_DELAY - (time.time() - self.last_request_dt), 0)
        if delay_time:
            await asyncio.sleep(delay_time)

    async def method(self, method: str, params: dict, timeout: float = 30):
        """
        Raises:
            aiohttp.ClientHttpProxyError: Неверный прокси.
        """
        await self._delay()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        url = "https://api.vk.com/method/" + method
        params['access_token'] = self.token
        params['v'] = self.v
        async with self.session.post(
                url,
                data=params,
                headers=headers,
                proxy=self.proxy,
                timeout=timeout,
                ssl=self.cert,
        ) as response:
            response = await response.json()
        if "error" in response:
            logging.error(response['error']["error_msg"])
        return response

    async def send(self, url: str, params: dict, wait: int = 25):
        async with self.session.get(url, params=params, proxy=self.proxy, timeout=wait + 10, ssl=self.cert) as response:
            response = await response.json()
        return response

    async def close(self):
        await self.session.close()
