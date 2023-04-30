import discord
import os
from cogs.debug import Debug
from cogs.economy import Economy
from cogs.income import Income
from logger import logger
from discord.ext import commands
from data.db_session import global_init
from initializers import guild_init


def bot_init(bot: discord.Bot):
    cogs = [Economy(bot), Income(bot), Debug(bot)]
    for cog in cogs:
        bot.add_cog(cog)


def main():
    bot = commands.Bot(intents=discord.Intents.default())
    global_init(os.path.join("db", "bot.db"))
    logger.info("db/bot.db initialized")
    bot_init(bot)

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        await guild_init(guild)

    @bot.event
    async def on_application_command_error(ctx: discord.ApplicationContext, exception:
                                           discord.DiscordException):
        if isinstance(exception, commands.NoPrivateMessage):
            embed = discord.Embed(
                title="Команду нельзя использовать",
                description="Данную команду нельзя использовать вне сервера.",
                color=0xAD1A1A
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Что-то пошло не так...",
                description="Что-то пошло не так во время выполнения команды, попробуйте позже\n"
                            f"{exception}"
            )
            await ctx.respond(embed=embed)

    bot.run()


if __name__ == "__main__":
    main()
