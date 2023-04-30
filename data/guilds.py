import sqlalchemy
from datetime import timedelta
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class DataGuild(SqlAlchemyBase):
    __tablename__ = "guilds"

    guild_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False, unique=True)
    currency = sqlalchemy.Column(sqlalchemy.String, default="$")
    start_balance_cash = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    start_balance_bank = sqlalchemy.Column(sqlalchemy.Integer, default=100)
    maximum_balance_cash = sqlalchemy.Column(sqlalchemy.Integer, default=1000000)
    maximum_balance_bank = sqlalchemy.Column(sqlalchemy.Integer, default=10000)

    cooldown_work = sqlalchemy.Column(sqlalchemy.Interval, default=timedelta(hours=24))
    cooldown_slut = sqlalchemy.Column(sqlalchemy.Interval, default=timedelta(hours=24))
    cooldown_crime = sqlalchemy.Column(sqlalchemy.Interval, default=timedelta(hours=24))
    cooldown_rob = sqlalchemy.Column(sqlalchemy.Interval, default=timedelta(hours=24))

    minimum_payout_work = sqlalchemy.Column(sqlalchemy.Integer, default=50)
    minimum_payout_slut = sqlalchemy.Column(sqlalchemy.Integer, default=50)
    minimum_payout_crime = sqlalchemy.Column(sqlalchemy.Integer, default=100)

    maximum_payout_work = sqlalchemy.Column(sqlalchemy.Integer, default=150)
    maximum_payout_slut = sqlalchemy.Column(sqlalchemy.Integer, default=150)
    maximum_payout_crime = sqlalchemy.Column(sqlalchemy.Integer, default=250)
    maximum_payout_percentage_rob = sqlalchemy.Column(sqlalchemy.Integer, default=30)

    fail_rate_slut = sqlalchemy.Column(sqlalchemy.Integer, default=5)
    fail_rate_crime = sqlalchemy.Column(sqlalchemy.Integer, default=40)
    fail_rate_rob = sqlalchemy.Column(sqlalchemy.Integer, default=40)

    fine_type_slut = sqlalchemy.Column(sqlalchemy.CHAR, default='x')
    fine_type_crime = sqlalchemy.Column(sqlalchemy.CHAR, default='x')
    fine_type_rob = sqlalchemy.Column(sqlalchemy.CHAR, default='x')

    fine_minimum_amount_slut = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    fine_minimum_amount_crime = sqlalchemy.Column(sqlalchemy.Integer, default=50)
    fine_minimum_amount_rob = sqlalchemy.Column(sqlalchemy.Integer, default=50)

    fine_maximum_amount_slut = sqlalchemy.Column(sqlalchemy.Integer, default=40)
    fine_maximum_amount_crime = sqlalchemy.Column(sqlalchemy.Integer, default=150)
    fine_maximum_amount_rob = sqlalchemy.Column(sqlalchemy.Integer, default=150)

    user = orm.relationship("DataUser", back_populates="guild")
