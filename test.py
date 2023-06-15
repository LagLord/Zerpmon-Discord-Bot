import asyncio

import config
import xrpl_functions


async def test():
    status, nfts = await xrpl_functions.get_nfts('')
    for nft in nfts:
        if nft["Issuer"] == config.ISSUER["Zerpmon"]:
            print(nft)
asyncio.run(test())