from blueshed.micro.orm.orm_utils import Base
from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column
from sqlalchemy.orm.mapper import validates


class Person(Base):

    id = Column(Integer, primary_key=True)
    email = Column(String(80), nullable=False, unique=True)
    password = Column(String(80))

    @validates('email')
    def validate_email(self, key, address):
        assert address is not None
        assert '@' in address
        return address
