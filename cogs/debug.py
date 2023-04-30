import discord
from discord.ext import commands
from data.db_session import create_session
from data.users import DataUser
from data.guilds import DataGuild
from logger import logger
from initializers import guild_init, user_init


class Debug(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("Debug Cog initialized")

    emulate_guild_init_params = {
        "name": "emulate-guild-init",
        "options": [
            discord.Option(
                str,
                name="replace",
                required=False,
                default=False,
                choices=[
                    discord.OptionChoice("True", "True"),
                    discord.OptionChoice("False", "False")
                ]
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**emulate_guild_init_params)
    async def emulate_guild_init(self, ctx: discord.ApplicationContext, replace):
        await guild_init(ctx.guild, replace)
        await ctx.respond("Success")

    emulate_user_init_params = {
        "name": "emulate-user-init",
        "options": [
            discord.Option(
                str,
                name="replace",
                required=False,
                default=False,
                choices=[
                    discord.OptionChoice("True", "True"),
                    discord.OptionChoice("False", "False")
                ]
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**emulate_user_init_params)
    async def emulate_user_init(self, ctx: discord.ApplicationContext, replace):
        await user_init(ctx.user, ctx.guild, replace)
        await ctx.respond("Success")

