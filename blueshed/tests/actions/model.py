from blueshed.micro.utils.orm_utils import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String
from blueshed.micro.utils.json_encoded_dict import JSONEncodedDict


class User(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128))
    password = Column(String(80))


class Group(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))


class Log(Base):
    id = Column(Integer, primary_key=True)
    signal = Column(String(255))
    message = Column(JSONEncodedDict())
    created = Column(String(255))
    created_by = Column(Integer)
