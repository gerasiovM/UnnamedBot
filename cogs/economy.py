import discord
from discord.ext import commands
from data.db_session import create_session
from data.users import DataUser
from data.guilds import DataGuild
from logger import logger
from checks import check_user_exists, check_user_has_enough
from initializers import user_init
from currency_operations import manage_bank


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("Economy Cog initialized")

    set_currency_params = {
        "name": "set-currency",
        "description": "Команда для установки валюты. Использовать без аргументов, "
                       "чтобы увидеть какой символ установлен.",
        "options": [
            discord.Option(
                str,
                name="symbol",
                description="Символ, который будет использовать в качестве валюты",
                min_length=1,
                required=False,
                default=None
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_currency_params)
    async def set_currency(self, ctx: discord.ApplicationContext, symbol):
        logger.debug("Setting currency")
        session = create_session()
        guild_id = ctx.guild_id
        if symbol is None:
            logger.debug("Symbol is None")
            symbol = session.get(DataGuild, guild_id).currency
            embed = discord.Embed(
                title="Информация о валюте",
                description=f"Текущая валюта: {symbol}",
                color=0x3498DB)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            logger.debug(f"Symbol is {symbol}")
            guild = session.get(DataGuild, guild_id)
            guild.currency = symbol
            session.commit()
            embed = discord.Embed(title="Валюта установлена",
                                  description="Ваша валюта была успешно установлена",
                                  color=0x2ECC71)
            await ctx.respond(embed=embed, ephemeral=True)

    set_maximum_balance_params = {
        "name": "set-maximum-balance",
        "description": "Установить максимальный баланс для руки или банка",
        "options": [
            discord.Option(
                str,
                name="type",
                description="Тип хранения. Cash для руки, Bank для банка",
                required=True,
                choices=[
                    discord.OptionChoice("Cash", "cash"),
                    discord.OptionChoice("Bank", "bank")
                ]
            ),
            discord.Option(
                int,
                name="amount",
                description="Количество валюты",
                max_value=100000000,
                min_value=1,
                required=False,
                default=None
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_maximum_balance_params)
    async def set_maximum_balance(self, ctx, choice, amount):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        currency = data_guild.currency
        if amount is None:
            if choice == "cash":
                amount = data_guild.maximum_balance_cash
                embed = discord.Embed(
                    title="Максимальное количество валюты",
                    description=f"Текущий максимум в руке: {amount} {currency}",
                    color=0x3498DB)
            else:
                amount = data_guild.maximum_balance_bank
                embed = discord.Embed(
                    title="Максимальное количество валюты",
                    description=f"Текущий максимум в банке: {amount} {currency}",
                    color=0x3498DB)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if choice == "cash":
                data_guild.maximum_balance_cash = amount
                embed = discord.Embed(
                    title="Максимальное количество валюты",
                    description=f"Максимальное количество в руке установлено: {amount}"
                                f" {currency}",
                    color=0x2ECC71)
            else:
                data_guild.maximum_balance_bank = amount
                embed = discord.Embed(
                    title="Максимальное количество валюты",
                    description=f"Максимальное количество в банке установлено: {amount}"
                                f" {currency}",
                    color=0x2ECC71)
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    set_start_balance_params = {
        "name": "set-start-balance",
        "description": "Установить стартовый баланс для руки или банка",
        "options": [
            discord.Option(
                str,
                name="type",
                description="Тип хранения. cash|bank",
                required=True,
                choices=[
                    discord.OptionChoice("cash", "cash"),
                    discord.OptionChoice("bank", "bank")
                ]
            ),
            discord.Option(
                int,
                name="amount",
                description="Количество валюты",
                min_value=1,
                max_value=100000000,
                required=False,
                default=None
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_start_balance_params)
    async def set_start_balance(self, ctx, choice, amount):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        currency = data_guild.currency
        if amount is None:
            if choice == "cash":
                amount = data_guild.start_balance_cash
                embed = discord.Embed(
                    title="Стартовое количество валюты",
                    description=f"Текущий стартовый баланс в руке: {amount} {currency}",
                    color=0x3498DB)
            else:
                amount = data_guild.start_balance_bank
                embed = discord.Embed(
                    title="Стартовое количество валюты",
                    description=f"Текущий стартовый баланс в банке: {amount} {currency}",
                    color=0x3498DB)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if choice == "cash":
                data_guild.start_balance_cash = amount
                embed = discord.Embed(
                    title="Стартовое количество валюты",
                    description=f"Стартовый баланс для руки установлен: {amount} {currency}",
                    color=0x2ECC71)
            else:
                data_guild.start_balance_bank = amount
                embed = discord.Embed(
                    title="Стартовое количество валюты",
                    description=f"Стартовый баланс для банка установлен: {amount} {currency}",
                    color=0x2ECC71)
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    balance_params = {
        "name": "balance",
        "description": "Проверь сколько денег есть у тебя или кого-то другого",
        "options": [
            discord.Option(
                discord.Member,
                name="member",
                description="Пользователь, баланс которого вы хотите посмотреть.",
                required=False,
                default=None,
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**balance_params)
    async def balance(self, ctx: discord.ApplicationContext, member: discord.Member):
        session = create_session()
        if member is None:
            user = ctx.user
        else:
            user = member._user
        guild = ctx.guild
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = session.get(DataGuild, guild.id)
        cash = data_user.cash
        bank = data_user.bank
        currency = data_guild.currency
        embed = discord.Embed(
            title="Баланс пользователя"
        )
        embed.add_field(
            name="Cash",
            value=f"{cash} {currency}"
        )
        embed.add_field(
            name="Bank",
            value=f"{bank} {currency}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    deposit_params = {
        "name": "deposit",
        "description": "Положи свои деньги на счет в банке",
        "options": [
            discord.Option(
                int,
                name="amount",
                description="Количество валюты, которое вы хотите положить в банк",
                required=True,
                min_value=1,
                max_value=10000000
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**deposit_params)
    async def deposit(self, ctx: discord.ApplicationContext, amount):
        session = create_session()
        user = ctx.user
        guild = ctx.guild
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = data_user.guild
        currency = data_guild.currency
        if not check_user_has_enough(data_user, amount, "cash"):
            embed = discord.Embed(
                title="Недостаточно средств",
                description=f"Вы не можете положить в банк {amount} {currency}, так как у вас всего"
                            f" {data_user.cash} {currency}"
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        await manage_bank(data_user, data_guild, amount, "deposit")
        session.commit()
        embed = discord.Embed(
            title="Успешный взнос",
            description=f"Вы успешно перевели {amount} {currency} на свой банковский счет, "
                        f"теперь у вас на счету {data_user.bank} {currency}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    withdraw_params = {
        "name": "withdraw",
        "description": "Возьми денег со своего счета в банке",
        "options": [
            discord.Option(
                int,
                name="amount",
                description="Количество валюты, которое вы хотите взять из банка",
                required=True,
                min_value=1,
                max_value=10000000
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**withdraw_params)
    async def withdraw(self, ctx: discord.ApplicationContext, amount):
        session = create_session()
        user = ctx.user
        guild = ctx.guild
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = data_user.guild
        currency = data_guild.currency
        if not check_user_has_enough(data_user, amount, "bank"):
            embed = discord.Embed(
                title="Недостаточно средств",
                description=f"Вы не можете взять из банка {amount} {currency}, так как у вас всего"
                            f" {data_user.bank} {currency}"
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        await manage_bank(data_user, data_guild, amount, "withdraw")
        session.commit()
        embed = discord.Embed(
            title="Успешное снятие",
            description=f"Вы успешно сняли {amount} {currency} со своего банковского счета, "
                        f"теперь у вас на руке {data_user.cash} {currency}"
        )
        await ctx.respond(embed=embed, ephemeral=True)
