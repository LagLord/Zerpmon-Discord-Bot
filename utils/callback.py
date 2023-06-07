import asyncio

import nextcord
from nextcord import ButtonStyle
from nextcord.ui import Button, View

import config
import db_query
import xumm_functions


async def purchase_callback(_i: nextcord.Interaction, amount, qty=1):
    try:
        await _i.edit(content="Generating transaction QR code...", embeds=[], view=None)
    except:
        await _i.send(content="Generating transaction QR code...", ephemeral=True)
    user_id = str(_i.user.id)
    if amount == config.POTION[0]:
        config.revive_potion_buyers[user_id] = qty
    else:
        config.mission_potion_buyers[user_id] = qty
    send_amt = (amount * qty) if str(user_id) in config.store_24_hr_buyers else (amount * (qty - 1 / 2))
    user_address = db_query.get_owned(_i.user.id)['address']
    uuid, url, href = await xumm_functions.gen_txn_url(config.STORE_ADDR, user_address, send_amt * 10 ** 6)
    embed = nextcord.Embed(color=0x01f39d, title=f"Please sign the transaction using this QR code or click here.",
                           url=href)

    embed.set_image(url=url)

    await _i.send(embed=embed, ephemeral=True, )

    for i in range(18):
        if user_id in config.latest_purchases:
            config.latest_purchases.remove(user_id)
            await _i.send(embed=nextcord.Embed(title="**Success**",
                                               description=f"Bought **{qty}** {'Revive All Potion' if amount in [8.99, 4.495] else 'Mission Refill Potion'}",
                                               ), ephemeral=True)
        await asyncio.sleep(10)


async def show_store(interaction: nextcord.Interaction):
    user = interaction.user

    user_owned_nfts = db_query.get_owned(user.id)
    main_embed = nextcord.Embed(title="Store Holdings", color=0xfcff82)
    # Sanity checks

    for owned_nfts in [user_owned_nfts]:
        if owned_nfts is None:
            main_embed.description = \
                f"Sorry no NFTs found for **{interaction.user.name}** or haven't yet verified your wallet"
            return main_embed
        if 'revive_potion' not in owned_nfts and 'mission_potion' not in owned_nfts:
            main_embed.description = \
                f"Sorry you don't have any Revive or Mission refill potions purchase one from `/store`"
            return main_embed

    main_embed.add_field(name="Revive All Potions: ",
                         value=f"**{0 if 'revive_potion' not in user_owned_nfts else user_owned_nfts['revive_potion']}**"
                               + '\t🍹',
                         inline=False)
    main_embed.add_field(name="Mission Refill Potions: ",
                         value=f"**{0 if 'mission_potion' not in user_owned_nfts else user_owned_nfts['mission_potion']}**"
                               + '\t🍶',
                         inline=False)

    main_embed.add_field(name="XRP Earned: ",
                         value=f"**{0 if 'xrp_earned' not in user_owned_nfts else user_owned_nfts['xrp_earned']}**"
                         ,
                         inline=False)
    main_embed.set_footer(text=f"Usage guide: \n"
                               f"/use revive_potion zerpmon_id\n"
                               f"/use mission_refill\n")
    return main_embed


async def store_callback(interaction: nextcord.Interaction):
    user_id = interaction.user.id
    main_embed = nextcord.Embed(title="Zerpmon Store", color=0xfcff82)
    main_embed.add_field(name="**Revive All Potions**" + '\t🍹',
                         value=f"Cost: `{config.POTION[0]} XRP`" if str(user_id) in config.store_24_hr_buyers else
                         f"Cost: `{config.POTION[0] / 2:.5f} XRP` \n(🥳 Half price for first purchase every 24hr 🥳)",
                         inline=False)
    main_embed.add_field(name="**Mission Refill Potions**" + '\t🍶',
                         value=f"Cost: `{config.MISSION_REFILL[0]} XRP`" if str(
                             user_id) in config.store_24_hr_buyers else
                         f"Cost: `{config.MISSION_REFILL[0] / 2:.5f} XRP` \n(🥳 Half price for first purchase every 24hr 🥳)",
                         inline=False)

    main_embed.add_field(name=f"\u200B",
                         value="**Purchase Guide**",
                         inline=False)
    main_embed.add_field(name=f"\u200B",
                         value=f"For getting access to one of these potions send the **exact** amount in **XRP** to "
                         ,
                         inline=False)
    main_embed.add_field(name=f"**`{config.STORE_ADDR}`** ",
                         value=f"or use `/buy revive_potion`, `/buy mission_refill` to buy "
                               f"using earned XRP",
                         inline=False)
    main_embed.add_field(name=f"\u200B",
                         value=f"Items will be available within a few minutes after transaction is successful",
                         inline=False)

    main_embed.set_footer(text=f"Usage guide: \n"
                               f"/use revive_potion\n"
                               f"/use mission_refill")

    sec_embed = await show_store(interaction)

    b1 = Button(label="Buy Revive All Potion", style=ButtonStyle.blurple)
    b2 = Button(label="Buy Mission Refill Potion", style=ButtonStyle.blurple)
    view = View()
    view.add_item(b1)
    view.add_item(b2)
    view.timeout = 120  # Set a timeout of 60 seconds for the view to automatically remove it after the time is up

    # Add the button callback to the button
    b1.callback = lambda i: purchase_callback(i, config.POTION[0])
    b2.callback = lambda i: purchase_callback(i, config.MISSION_REFILL[0])

    await interaction.send(embeds=[main_embed, sec_embed], ephemeral=True, view=view)


async def use_missionP_callback(interaction: nextcord.Interaction):
    user = interaction.user
    user_id = user.id
    user_owned_nfts = {'data': db_query.get_owned(user.id), 'user': user.name}

    # Sanity checks
    if user.id in config.ongoing_battles:
        await interaction.send(f"Please wait, potions can't be used during a Battle.",
                               ephemeral=True)
        return

    for owned_nfts in [user_owned_nfts]:
        if owned_nfts['data'] is None:
            await interaction.send(
                f"Sorry no NFTs found for **{owned_nfts['user']}** or haven't yet verified your wallet", ephemeral=True)
            return

        if 'mission_potion' not in owned_nfts['data'] or int(owned_nfts['data']['mission_potion']) <= 0:
            return (await store_callback(interaction))

    saved = db_query.mission_refill(user_id)
    if not saved:
        await interaction.send(
            f"**Failed**",
            ephemeral=True)
        return False
    else:
        await interaction.send(
            f"**Success**",
            ephemeral=True)
        return True


async def use_reviveP_callback(interaction: nextcord.Interaction):
    user = interaction.user

    user_owned_nfts = {'data': db_query.get_owned(user.id), 'user': user.name}

    # Sanity checks
    if user.id in config.ongoing_battles:
        await interaction.send(f"Please wait, potions can't be used during a Battle.",
                               ephemeral=True)
        return

    for owned_nfts in [user_owned_nfts]:
        if owned_nfts['data'] is None:
            await interaction.send(
                f"Sorry no NFTs found for **{owned_nfts['user']}** or haven't yet verified your wallet", ephemeral=True)
            return

        if len(owned_nfts['data']['zerpmons']) == 0:
            await interaction.send(
                f"Sorry **0** Zerpmon found for **{owned_nfts['user']}**, need **1** to revive",
                ephemeral=True)
            return

        if 'revive_potion' not in owned_nfts['data'] or int(owned_nfts['data']['revive_potion']) <= 0:
            # await interaction.send(
            #     f"Sorry **0** Revive All Potions found for **{owned_nfts['user']}**, need **1** to revive Zerpmon",
            #     ephemeral=True)
            return (await store_callback(interaction))

    # await interaction.send(
    #     f"**Reviving all Zerpmon...**",
    #     ephemeral=True)
    saved = db_query.revive_zerpmon(user.id)
    if not saved:
        await interaction.send(
            f"**Failed**",
            ephemeral=True)
        return False
    else:
        await interaction.send(
            f"**Success**",
            ephemeral=True)
        return True

