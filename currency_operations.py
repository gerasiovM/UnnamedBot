from random import randint
from math import ceil
import discord
from datetime import datetime
from data.users import DataUser
from data.guilds import DataGuild


async def set_currency(data_user: DataUser, data_guild: DataGuild, amount, storage_type):
    if storage_type == "bank":
        maximum = data_guild.maximum_balance_bank
        data_user.bank = max(min(maximum, amount), 0)
    elif storage_type == "cash":
        maximum = data_guild.maximum_balance_cash
        data_user.cash = max(min(maximum, amount), 0)
    else:
        raise ValueError(f"Wrong storage type. Expected bank|cash, got {storage_type}")


async def add_currency(data_user: DataUser, data_guild: DataGuild, amount, amount_type,
                       storage_type):
    if storage_type == "bank":
        base_amount = data_user.bank
    elif storage_type == "cash":
        base_amount = data_user.cash
    else:
        raise ValueError(f"Wrong storage type. Expected bank|cash, got {storage_type}")
    if amount_type == "%":
        final_amount = base_amount + round(base_amount * amount)
    elif amount_type == "x":
        final_amount = base_amount + amount
    else:
        raise ValueError(f"Wrong amount type. Expected %|x, got {amount_type}")
    await set_currency(data_user, data_guild, final_amount, storage_type)


async def remove_currency(data_user: DataUser, data_guild: DataGuild, amount,
                          amount_type, storage_type):
    if storage_type == "bank":
        base_amount = data_user.bank
    elif storage_type == "cash":
        base_amount = data_user.cash
    else:
        raise ValueError(f"Wrong storage type. Expected bank|cash, got {storage_type}")
    if amount_type == "%":
        final_amount = base_amount - round(base_amount * amount)
    elif amount_type == "x":
        final_amount = base_amount - amount
    else:
        raise ValueError(f"Wrong amount type. Expected %|x, got {amount_type}")
    await set_currency(data_user, data_guild, final_amount, storage_type)


async def manage_income(data_user: DataUser, data_guild: DataGuild, income_type):
    if income_type == "work":
        amount = randint(data_guild.minimum_payout_work, data_guild.maximum_payout_work + 1)
        await add_currency(data_user, data_guild, amount, "x", "cash")
        data_user.last_work = datetime.utcnow()
        return {'success': True, 'amount': amount}
    elif income_type == "slut":
        percentage = randint(1, 101)
        if percentage <= data_guild.fail_rate_slut:
            amount = randint(data_guild.fine_minimum_amount_slut,
                             data_guild.fine_maximum_amount_slut + 1)
            await remove_currency(data_user, data_guild, amount, data_guild.fine_type_slut,
                                  "cash")
            data_user.last_slut = datetime.utcnow()
            return {'success': False, 'amount': amount}
        else:
            amount = randint(data_guild.minimum_payout_slut, data_guild.maximum_payout_slut + 1)
            await add_currency(data_user, data_guild, amount, "x", "cash")
            data_user.last_slut = datetime.utcnow()
            return {'success': True, 'amount': amount}
    elif income_type == "crime":
        percentage = randint(1, 101)
        if percentage <= data_guild.fail_rate_crime:
            amount = randint(data_guild.fine_minimum_amount_crime,
                             data_guild.fine_maximum_amount_crime + 1)
            await remove_currency(data_user, data_guild, amount, data_guild.fine_type_crime,
                                  "cash")
            data_user.last_crime = datetime.utcnow()
            return {'success': False, 'amount': amount}
        else:
            amount = randint(data_guild.minimum_payout_crime, data_guild.maximum_payout_crime + 1)
            await add_currency(data_user, data_guild, amount, "x", "cash")
            data_user.last_crime = datetime.utcnow()
            return {'success': True, 'amount': amount}
    else:
        raise ValueError(f"Wrong income type. Expected work|slut|crime, got {income_type}")


async def manage_rob(data_user1: DataUser, data_user2: DataUser, data_guild: DataGuild):
    cash1 = data_user1.cash
    cash2 = data_user2.cash
    minimum = ceil(cash2 / 100)
    if cash1 < minimum:
        return {'success': -1, 'amount': None, 'minimum': minimum}
    if cash2 < 100:
        return {'success': -2, 'amount': None}
    percentage = randint(1, 101)
    if percentage < data_guild.fail_rate_rob:
        amount = randint(data_guild.fine_minimum_amount_rob, data_guild.fine_maximum_amount_rob + 1)
        await remove_currency(data_user1, data_guild, amount, data_guild.fine_type_rob, "cash")
        return {'success': 0, 'amount': amount}
    else:
        amount = min(data_guild.maximum_payout_percentage_rob, round(cash1 / cash2) * 100)
        real_amount = round(data_user2.cash * amount / 100)
        await remove_currency(data_user2, data_guild, real_amount, "x", "cash")
        await add_currency(data_user1, data_guild, real_amount, "%", "cash")
        return {'success': 1, 'amount': real_amount}


async def manage_bank(data_user: DataUser, data_guild: DataGuild, amount, action):
    if action == "deposit":
        await add_currency(data_user, data_guild, amount, "x", "bank")
        await remove_currency(data_user, data_guild, amount, "x", "cash")
    elif action == "withdraw":
        await add_currency(data_user, data_guild, amount, "x", "cash")
        await remove_currency(data_user, data_guild, amount, "x", "bank")
    else:
        raise ValueError(f"Wrong action. Expected deposit|withdraw, got {action}")
