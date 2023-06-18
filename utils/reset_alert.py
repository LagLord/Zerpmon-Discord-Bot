import asyncio
import logging
import time
import traceback

import nextcord
from utils.checks import get_next_ts


async def send_reset_message(client: nextcord.Client):
    while True:
        await asyncio.sleep(20)
        reset_time = get_next_ts() - time.time()
        # print(reset_time)
        if reset_time < 60:
            await asyncio.sleep(60)
            guilds = client.guilds
            for guild in guilds:
                try:
                    channel = nextcord.utils.get(guild.channels, name="🌐│zerpmon-center")
                    await channel.send('@everyone, Global Missions, Zerpmon, Store prices restored.')
                except Exception as e:
                    logging.error(f'ERROR: {traceback.format_exc()}')
                time.sleep(5)
