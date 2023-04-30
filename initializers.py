import discord
from logger import logger
from checks import check_guild_exists, check_user_exists
from data.db_session import create_session
from data.guilds import DataGuild
from data.users import DataUser


async def guild_init(guild: discord.Guild, replace=False):
    session = create_session()
    data_guild = DataGuild()
    data_guild.guild_id = guild.id
    if replace:
        check_guild_exists(guild, delete=True)
    session.add(data_guild)
    session.commit()
    logger.debug(f"Added guild with id '{guild.id}'")


async def user_init(user: discord.User, guild: discord.Guild, replace=False):
    session = create_session()
    data_user = DataUser()
    data_user.user_id = user.id
    data_user.guild_id = guild.id
    data_user.cash = session.get(DataGuild, guild.id).start_balance_cash
    data_user.bank = session.get(DataGuild, guild.id).start_balance_bank
    if replace:
        check_user_exists(user, delete=True)
    session.add(data_user)
    session.commit()
    logger.debug(f"Added user with id '{user.id}' from guild '{guild.id}'")
