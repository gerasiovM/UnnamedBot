import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class DataUser(SqlAlchemyBase):
    __tablename__ = "users"

    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    guild_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("guilds.guild_id"),
                                 primary_key=True, nullable=False)
    cash = sqlalchemy.Column(sqlalchemy.Integer)
    bank = sqlalchemy.Column(sqlalchemy.Integer)
    last_work = sqlalchemy.Column(sqlalchemy.DateTime)
    last_slut = sqlalchemy.Column(sqlalchemy.DateTime)
    last_crime = sqlalchemy.Column(sqlalchemy.DateTime)
    last_rob = sqlalchemy.Column(sqlalchemy.DateTime)

    guild = orm.relationship("DataGuild")
