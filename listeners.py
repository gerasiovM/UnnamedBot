import discord
from discord.ext import commands
from initializers import guild_init


async def on_guild_join(guild: discord.Guild):
    await guild_init(guild)


async def on_application_command_error(ctx: discord.ApplicationContext, exception:
                                       discord.DiscordException):
    if isinstance(exception, commands.NoPrivateMessage):
        embed = discord.Embed(
            title="Команду нельзя использовать",
            description="Данную команду нельзя использовать вне сервера.",
            color=0xAD1A1A
        )
        await ctx.respond(embed=embed, ephemeral=True)