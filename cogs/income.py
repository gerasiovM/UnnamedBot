import datetime
import discord
from discord.ext import commands
from datetime import timedelta
from random import randint
from data.db_session import create_session
from data.users import DataUser
from data.guilds import DataGuild
from logger import logger
from format_timedelta import format_timedelta
from initializers import user_init
from checks import check_user_exists, check_user_can_do_action
from currency_operations import manage_income, manage_rob


class Income(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.debug("Income Cog initialized")

    set_cooldown_params = {
        "name": "set-cooldown",
        "description": "Установить перерыв для заработка",
        "options": [
            discord.Option(
                str,
                name="work_type",
                description="Тип заработка. work|slut|crime|rob",
                required=True,
                choices=[
                    discord.OptionChoice("work", "work"),
                    discord.OptionChoice("slut", "slut"),
                    discord.OptionChoice("crime", "crime"),
                    discord.OptionChoice("rob", "rob")
                ]
            ),
            discord.Option(
                int,
                name="amount",
                description="Количество единиц времени",
                min_length=1,
                max_length=4,
                min_value=1,
                required=False,
                default=None
            ),
            discord.Option(
                str,
                name="time",
                description="Какие единицы времени использовать. seconds|minutes|hours|days. "
                            "hours, если ничего не выбрать",
                required=False,
                default="hours",
                choices=[
                    discord.OptionChoice("seconds", "seconds"),
                    discord.OptionChoice("minutes", "minutes"),
                    discord.OptionChoice("hours", "hours"),
                    discord.OptionChoice("days", "days")
                ]
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_cooldown_params)
    async def set_cooldown(self, ctx: discord.ApplicationContext, work_type: str, amount: int,
                           time_choice: str):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        if amount is None:
            if work_type == "work":
                time = format_timedelta(data_guild.cooldown_work)
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Перерыв между работой: {time}",
                    color=0x3498DB
                )
            elif work_type == "slut":
                time = format_timedelta(data_guild.cooldown_slut)
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Перерыв между проституцией: {time}",
                    color=0x3498DB
                )
            elif work_type == "crime":
                time = format_timedelta(data_guild.cooldown_crime)
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Перерыв между преступлением: {time}",
                    color=0x3498DB
                )
            else:
                time = format_timedelta(data_guild.cooldown_rob)
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Перерыв между ограблением: {time}",
                    color=0x3498DB
                )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if time_choice == "seconds":
                time = timedelta(seconds=amount)
            elif time_choice == "minutes":
                time = timedelta(minutes=amount)
            elif time_choice == "days":
                time = timedelta(days=amount)
            else:
                time = timedelta(hours=amount)

            if work_type == "work":
                data_guild.cooldown_work = time
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Установлен перерыв между работой: {format_timedelta(time)}",
                    color=0x2ECC71
                )
            elif work_type == "slut":
                data_guild.cooldown_slut = time
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Установлен перерыв между проституцией: {format_timedelta(time)}",
                    color=0x2ECC71
                )
            elif work_type == "crime":
                data_guild.cooldown_crime = time
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Установлен перерыв между преступлением: {format_timedelta(time)}",
                    color=0x2ECC71
                )
            else:
                data_guild.cooldown_rob = time
                embed = discord.Embed(
                    title="Перерыв между действием",
                    description=f"Установлен перерыв между ограблением: {format_timedelta(time)}",
                    color=0x2ECC71
                )
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    set_fine_type_params = {
        "name": "set-fine-type",
        "description": "Установить тип штрафа при неудаче в процентах или числах",
        "options": [
            discord.Option(
                str,
                name="work_type",
                description="Тип заработка. slut|crime|rob",
                required=True,
                choices=[
                    discord.OptionChoice("slut", "slut"),
                    discord.OptionChoice("crime", "crime"),
                    discord.OptionChoice("rob", "rob")
                ]
            ),
            discord.Option(
                str,
                name="fine_type",
                description="Тип штрафа. %|x",
                required=False,
                default=None,
                choices=[
                    discord.OptionChoice("%", "%"),
                    discord.OptionChoice("x", "x")
                ]
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_fine_type_params)
    async def set_fine_type(self, ctx: discord.ApplicationContext, work_type, fine_type):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        if fine_type is None:
            if work_type == "slut":
                fine_type = data_guild.fine_type_slut
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Тип штрафа для проституции: {fine_type}",
                    color=0x3498DB
                )
            elif work_type == "crime":
                fine_type = data_guild.fine_type_crime
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Тип штрафа для преступления: {fine_type}",
                    color=0x3498DB
                )
            else:
                fine_type = data_guild.fine_type_rob
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Тип штрафа для ограбления: {fine_type}",
                    color=0x3498DB
                )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if work_type == "slut":
                data_guild.fine_type_slut = fine_type
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Установлен тип штрафа для проституции: {fine_type}",
                    color=0x2ECC71
                )
            elif work_type == "crime":
                data_guild.fine_type_crime = fine_type
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Установлен тип штрафа для преступления: {fine_type}",
                    color=0x2ECC71
                )
            else:
                data_guild.fine_type_rob = fine_type
                embed = discord.Embed(
                    title="Тип штрафа действия",
                    description=f"Установлен тип штрафа для ограбления: {fine_type}",
                    color=0x2ECC71
                )
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    set_fine_amount_params = {
        "name": "set-fine-amount",
        "description": "Установить штраф за действие",
        "options": [
            discord.Option(
                str,
                name="work_type",
                description="Тип заработка. slut|crime|rob",
                required=True,
                choices=[
                    discord.OptionChoice("slut", "slut"),
                    discord.OptionChoice("crime", "crime"),
                    discord.OptionChoice("rob", "rob")
                ]),
            discord.Option(
                str,
                name="min_max",
                description="Граница штрафа. min|max",
                required=True,
                choices=[
                    discord.OptionChoice("min", "min"),
                    discord.OptionChoice("max", "max")
                ]
            ),
            discord.Option(
                int,
                name="amount",
                description="Количество валюты",
                required=False,
                default=None,
                min_value=0,
                max_value=100000000
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_fine_amount_params)
    async def set_fine_amount(self, ctx: discord.ApplicationContext, work_type, min_max, amount):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        if amount is None:
            if min_max == "min":
                if work_type == "slut":
                    fine_amount = data_guild.fine_minimum_amount_slut
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Минимальная граница штрафа для проституции: {fine_amount}",
                        color=0x3498DB
                    )
                elif work_type == "crime":
                    fine_amount = data_guild.fine_minimum_amount_crime
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Минимальная граница штрафа для преступления: {fine_amount}",
                        color=0x3498DB
                    )
                else:
                    fine_amount = data_guild.fine_minimum_amount_rob
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Минимальная граница штрафа для ограбления: {fine_amount}",
                        color=0x3498DB
                    )
            else:
                if work_type == "slut":
                    fine_amount = data_guild.fine_maximum_amount_slut
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Максимальная граница штрафа для проституции: {fine_amount}",
                        color=0x3498DB
                    )
                elif work_type == "crime":
                    fine_amount = data_guild.fine_maximum_amount_crime
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Максимальная граница штрафа для преступления: {fine_amount}",
                        color=0x3498DB
                    )
                else:
                    fine_amount = data_guild.fine_maximum_amount_rob
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Максимальная граница штрафа для ограбления: {fine_amount}",
                        color=0x3498DB
                    )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if min_max == "min":
                if work_type == "slut":
                    data_guild.fine_minimum_amount_slut = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена минимальная граница штрафа для проституции:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
                elif work_type == "crime":
                    data_guild.fine_minimum_amount_crime = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена минимальная граница штрафа для преступления:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
                else:
                    data_guild.fine_minimum_amount_rob = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена минимальная граница штрафа для ограбления:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
            else:
                if work_type == "slut":
                    data_guild.fine_maximum_amount_slut = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена максимальная граница штрафа для проституции:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
                elif work_type == "crime":
                    data_guild.fine_maximum_amount_crime = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена максимальная граница штрафа для преступления:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
                else:
                    data_guild.fine_maximum_amount_rob = amount
                    embed = discord.Embed(
                        title="Граница штрафа",
                        description=f"Установлена максимальная граница штрафа для ограбления:"
                                    f" {amount}",
                        color=0x2ECC71
                    )
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    set_fail_rate_params = {
        "name": "set-fail-rate",
        "description": "Установить процент неудачи для действий",
        "options": [
            discord.Option(
                str,
                name="work_type",
                description="Тип заработка. slut|crime|rob",
                required=True,
                choices=[
                    discord.OptionChoice("slut", "slut"),
                    discord.OptionChoice("crime", "crime"),
                    discord.OptionChoice("rob", "rob")
                ]),
            discord.Option(
                int,
                name="percentage",
                description="Процент неудачи",
                required=False,
                default=None,
                min_value=0,
                max_value=100
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**set_fail_rate_params)
    async def set_fail_rate(self, ctx: discord.ApplicationContext, work_type, percentage):
        session = create_session()
        data_guild = session.get(DataGuild, ctx.guild.id)
        if percentage is None:
            if work_type == "slut":
                percentage = data_guild.fail_rate_slut
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Процент неудачи для проституции: {percentage}%",
                    color=0x3498DB
                )
            elif work_type == "crime":
                percentage = data_guild.fail_rate_crime
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Процент неудачи для преступления: {percentage}%",
                    color=0x3498DB
                )
            else:
                percentage = data_guild.fail_rate_rob
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Процент неудачи для ограбления: {percentage}%",
                    color=0x3498DB
                )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if work_type == "slut":
                data_guild.fail_rate_slut = percentage
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Установлен процент неудачи для проституции: {percentage}%",
                    color=0x2ECC71
                )
            elif work_type == "crime":
                data_guild.fail_rate_crime = percentage
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Установлен процент неудачи для преступления: {percentage}%",
                    color=0x2ECC71
                )
            else:
                data_guild.fail_rate_rob = percentage
                embed = discord.Embed(
                    title="Процент неудачи",
                    description=f"Установлен процент неудачи для ограбления: {percentage}%",
                    color=0x2ECC71
                )
            session.commit()
            await ctx.respond(embed=embed, ephemeral=True)

    work_params = {
        "name": "work",
        "description": "Поработай на дядю, подзаработай деньжат"
    }

    @commands.guild_only()
    @commands.slash_command(**work_params)
    async def work(self, ctx: discord.ApplicationContext):
        session = create_session()
        guild = ctx.guild
        user = ctx.author
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = session.get(DataGuild, guild.id)
        if not check_user_can_do_action(data_user, data_guild, "work"):
            remaining_time = data_user.last_work + data_guild.cooldown_work -\
                             datetime.datetime.utcnow()
            embed = discord.Embed(
                title="Прошло недостаточно времени",
                description="С момента последней работы прошло недостаточно "
                            f"времени.\n\nПодождите ещё "
                            f"{format_timedelta(remaining_time)}",
                color=0xAD1A1A
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        response = await manage_income(data_user, data_guild, "work")
        session.commit()
        await ctx.respond(f"Вы заработали на работе {response['amount']}"
                          f" {data_guild.currency}.\n"
                          f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")

    slut_params = {
        "name": "slut",
        "description": "Заработай нелегальных денег своим телом"
    }

    @commands.guild_only()
    @commands.slash_command(**slut_params)
    async def slut(self, ctx: discord.ApplicationContext):
        session = create_session()
        guild = ctx.guild
        user = ctx.user
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = session.get(DataGuild, guild.id)
        if not check_user_can_do_action(data_user, data_guild, "slut"):
            remaining_time = data_user.last_slut + data_guild.cooldown_slut -\
                             datetime.datetime.utcnow()
            embed = discord.Embed(
                title="Прошло недостаточно времени",
                description="С момента последней проституции прошло недостаточно "
                            f"времени.\n\nПодождите ещё "
                            f"{format_timedelta(remaining_time)}",
                color=0xAD1A1A
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        response = await manage_income(data_user, data_guild, "slut")
        session.commit()
        if not response['success']:
            await ctx.respond(f"Вы потеряли на проституции {response['amount']}"
                              f" {data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")
        else:
            await ctx.respond(f"Вы заработали на проституции {response['amount']}"
                              f"{data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")

    crime_params = {
        "name": "crime",
        "description": "Обворуй музей, возьми золотишка"
    }

    @commands.guild_only()
    @commands.slash_command(**crime_params)
    async def crime(self, ctx: discord.ApplicationContext):
        session = create_session()
        guild = ctx.guild
        user = ctx.user
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = session.get(DataGuild, guild.id)
        if not check_user_can_do_action(data_user, data_guild, "crime"):
            remaining_time = data_user.last_crime + data_guild.cooldown_crime -\
                             datetime.datetime.utcnow()
            embed = discord.Embed(
                title="Прошло недостаточно времени",
                description="С момента последнего преступления прошло недостаточно "
                            f"времени.\n\nПодождите ещё "
                            f"{format_timedelta(remaining_time)}",
                color=0xAD1A1A
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        response = await manage_income(data_user, data_guild, "crime")
        session.commit()
        if not response['success']:
            await ctx.respond(f"Вы потеряли из-за преступления {response['amount']}"
                              f" {data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")
        else:
            await ctx.respond(f"Вы заработали на преступлении {response['amount']}"
                              f"{data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")

    rob_params = {
        "name": "rob",
        "description": "Ограбь простолюдина",
        "options": [
            discord.Option(
                discord.Member,
                name="member",
                description="Кого собираешься ограбить",
                required=True
            )
        ]
    }

    @commands.guild_only()
    @commands.slash_command(**rob_params)
    async def rob(self, ctx: discord.ApplicationContext, member: discord.Member):
        session = create_session()
        guild = ctx.guild
        user = ctx.user
        user2 = member._user
        if not check_user_exists(user, guild):
            await user_init(user, guild)
        if not check_user_exists(user2, guild):
            await user_init(user2, guild)
        data_user = session.get(DataUser, (user.id, guild.id))
        data_guild = session.get(DataGuild, guild.id)
        data_user2 = session.get(DataUser, (user2.id, guild.id))
        if not check_user_can_do_action(data_user, data_guild, "rob"):
            remaining_time = data_user.last_rob + data_guild.cooldown_rob - \
                             datetime.datetime.utcnow()
            embed = discord.Embed(
                title="Прошло недостаточно времени",
                description="С момента последнего ограбления прошло недостаточно "
                            f"времени.\n\nПодождите ещё "
                            f"{format_timedelta(remaining_time)}",
                color=0xAD1A1A
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        response = await manage_rob(data_user, data_user2, data_guild)
        session.commit()
        if response['success'] == -1:
            embed = discord.Embed(
                title="Недостаточно средств",
                description="У вас недостаточно средств, чтобы совершить ограбление.\n"
                            f"Вам нужно минимум {response['minimum']} {data_guild.currency}, чтобы "
                            f"ограбить {user2.mention}."
            )
            await ctx.respond(embed=embed, ephemeral=True)
        elif response['success'] == -2:
            embed = discord.Embed(
                title="Недостаточно средств",
                description=f"У {user2.mention} недостаточно средств"
            )
            await ctx.respond(embed=embed, ephemeral=True)
        elif response['success'] == 0:
            await ctx.respond(f"Вы потеряли на ограблении {user2.mention} {response['amount']}"
                              f" {data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")
        else:
            await ctx.respond(f"Вы заработали на ограблении {user2.mention} {response['amount']}"
                              f" {data_guild.currency}.\n"
                              f"Ваш нынешний баланс: {data_user.cash} {data_guild.currency}")
