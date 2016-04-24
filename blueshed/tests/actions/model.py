from blueshed.micro.utils.orm_utils import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String


class User(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128))
    password = Column(String(80))


class Group(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
