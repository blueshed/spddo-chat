from blueshed.micro.orm.orm_utils import Base
from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column


class Person(Base):

    id = Column(Integer, primary_key=True)
    email = Column(String(80))
    password = Column(String(80))
