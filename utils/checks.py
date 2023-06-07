import nextcord
import datetime
import pytz


async def get_time_left_utc():
    # Get current UTC time
    current_time = datetime.datetime.utcnow()

    # Calculate the time difference until the next UTC 00:00
    next_day = current_time + datetime.timedelta(days=1)
    target_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
    time_difference = target_time - current_time

    # Extract the hours and minutes from the time difference
    hours_left = time_difference.total_seconds() // 3600
    minutes_left = (time_difference.total_seconds() % 3600) // 60

    return int(hours_left), int(minutes_left)


def get_next_ts():
    # Get the current time in UTC
    current_time = datetime.datetime.now(pytz.utc)

    # Calculate the time difference until the next UTC 00:00
    next_day = current_time + datetime.timedelta(days=1)
    target_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
    return target_time.timestamp()


async def check_wager_entry(interaction: nextcord.Interaction, users):
    for owned_nfts in users:
        if owned_nfts['data'] is None:
            await interaction.send(
                f"Sorry no NFTs found for **{owned_nfts['user']}** or haven't yet verified your wallet")
            return False

        if len(owned_nfts['data']['zerpmons']) == 0:
            await interaction.send(
                f"Sorry **0** Zerpmon found for **{owned_nfts['user']}**, need **1** to start doing wager battles")
            return False

        if len(owned_nfts['data']['trainer_cards']) == 0:
            await interaction.send(
                f"Sorry **0** Trainer cards found for **{owned_nfts['user']}**, need **1** to start doing wager battles")
            return False
    return True


