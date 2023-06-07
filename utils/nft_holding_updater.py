import asyncio
import logging

import nextcord

import config
import xrpl_functions
import db_query
from datetime import date


async def check_and_reset_store():
    today = date.today()
    current_day = today.day
    if current_day != config.day:
        config.day = current_day
        config.store_24_hr_buyers = []


async def update_nft_holdings(client: nextcord.Client):
    while True:
        await asyncio.sleep(10)
        await check_and_reset_store()
        all_users = db_query.get_all_users()
        guilds = client.guilds

        for old_user in all_users:
            try:
                user_obj = old_user
                if 'address' not in user_obj:
                    continue
                good_status, nfts = await xrpl_functions.get_nfts(user_obj['address'])

                main_trainer = user_obj["main_trainer"] if 'main_trainer' in user_obj else ""
                mission_zerpmon = user_obj["mission_zerpmon"] if 'mission_zerpmon' in user_obj else ""
                battle_deck = user_obj["battle_deck"] if 'battle_deck' in user_obj else {}

                serials = []
                t_serial = []

                for nft in nfts:

                    if nft["Issuer"] == config.ISSUER["Trainer"]:

                        metadata = await xrpl_functions.get_nft_metadata(nft['URI'])
                        serial = str(nft["nft_serial"])

                        if "Zerpmon Trainers" in metadata['description']:
                            t_serial.append(serial)
                            # Add to MongoDB here
                            new_z = {"name": metadata['name'],
                                     "image": metadata['image'],
                                     "attributes": metadata['attributes'],
                                     "token_id": nft["NFTokenID"],
                                     }
                            if serial not in list(old_user['trainer_cards'].keys()):
                                db_query.add_user_nft(user_obj['discord_id'], serial, new_z, True)
                        await asyncio.sleep(2)
                    if nft["Issuer"] == config.ISSUER["Zerpmon"]:
                        metadata = await xrpl_functions.get_nft_metadata(nft['URI'])
                        serial = str(nft["nft_serial"])

                        if "Zerpmon " in metadata['description']:
                            serials.append(serial)
                            try:
                                active_t = user_obj["zerpmons"][serial]['active_t']
                            except:
                                active_t = 0
                            # Add to MongoDB here
                            new_z = {"name": metadata['name'],
                                     "image": metadata['image'],
                                     "attributes": metadata['attributes'],
                                     "token_id": nft["NFTokenID"],
                                     'active_t': active_t
                                     }
                            if serial not in list(old_user['zerpmons'].keys()):
                                db_query.add_user_nft(user_obj['discord_id'], serial, new_z, False)
                        await asyncio.sleep(2)
                for serial in list(old_user['zerpmons'].keys()):
                    if serial not in serials:
                        db_query.remove_user_nft(user_obj['discord_id'], serial, False)
                for serial in list(old_user['trainer_cards'].keys()):
                    if serial not in t_serial:
                        db_query.remove_user_nft(user_obj['discord_id'], serial, True)

                if len(user_obj['zerpmons']) > 0 or len(user_obj['trainer_cards']) > 0:
                    for guild in guilds:
                        if 'guild_id' not in user_obj or ('guild_id' in user_obj and user_obj['guild_id'] == guild.id):
                            try:
                                # await asyncio.sleep(1)
                                user = await guild.fetch_member(int(user_obj['discord_id']))
                                print(guild, user)
                                if user is not None:
                                    user_obj['guild_id'] = guild.id
                                    if len(user_obj['zerpmons']) > 0:
                                        try:
                                            role = nextcord.utils.get(guild.roles, name="Zerpmon Holder")
                                            await user.add_roles(role)
                                        except:
                                            print("USER already has the required role")
                                    if len(user_obj['trainer_cards']) > 0:
                                        try:
                                            role = nextcord.utils.get(guild.roles, name="Trainer")
                                            await user.add_roles(role)
                                        except:
                                            print("USER already has the required role")
                            except Exception as e:
                                print(f"USER already has the required role {e}")

                if mission_zerpmon not in serials:
                    mission_zerpmon = ""
                if main_trainer not in t_serial:
                    main_trainer = ""
                new_battle_deck = {'0': {}, '1': {}, '2': {}}
                for k, v in battle_deck.items():
                    for serial in v:
                        if serial == "trainer":
                            if v[serial] in t_serial:
                                new_battle_deck[k][serial] = v[serial]
                        if v[serial] in serials:
                            new_battle_deck[k][serial] = v[serial]

                logging.info(f'Serials {serials} \nnew deck: {new_battle_deck}')
                user_obj["main_trainer"] = main_trainer
                user_obj["mission_zerpmon"] = mission_zerpmon
                user_obj["battle_deck"] = new_battle_deck
            except Exception as e:
                logging.info(f"ERROR while updating NFTs: {e}")

            db_query.save_user({'main_trainer': user_obj["main_trainer"], 'mission_zerpmon': user_obj["mission_zerpmon"],
                                'battle_deck': user_obj["battle_deck"], 'discord_id': user_obj["discord_id"],
                                'username': user_obj["username"]})
            await asyncio.sleep(2)
        await asyncio.sleep(900)
