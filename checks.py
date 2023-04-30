import discord
from datetime import datetime
from data.db_session import create_session
from data.guilds import DataGuild
from data.users import DataUser


def check_guild_exists(guild: discord.Guild, delete=False):
    session = create_session()
    existing_data_guild = session.get(DataGuild, guild.id)
    if existing_data_guild:
        if delete:
            session.delete(existing_data_guild)
            session.commit()
        return True
    return False


def check_user_exists(user: discord.User, guild: discord.Guild, delete=False):
    session = create_session()
    existing_data_user = session.get(DataUser, (user.id, guild.id))
    if existing_data_user:
        if delete:
            session.delete(existing_data_user)
            session.commit()
        return True
    return False


def check_user_can_do_action(data_user: DataUser, data_guild: DataGuild, action):
    cooldown_map = {
        "work": "cooldown_work",
        "slut": "cooldown_slut",
        "crime": "cooldown_crime",
        "rob": "cooldown_rob"
    }
    last_time = getattr(data_user, f"last_{action}")
    if not last_time:
        return True
    interval = getattr(data_guild, cooldown_map[action])
    time_passed = datetime.utcnow() - last_time
    return time_passed >= interval


def check_user_has_enough(data_user: DataUser, amount, storage_type):
    if storage_type == "cash":
        return (data_user.cash - amount) >= 0
    elif storage_type == "bank":
        return (data_user.bank - amount) >= 0
    else:
        raise ValueError("Wrong storage type. Expected cash|bank, got " + storage_type)
