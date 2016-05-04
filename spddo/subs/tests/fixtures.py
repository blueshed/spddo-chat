from blueshed.micro.orm import db_connection, orm_utils
from spddo.subs.actions.context import Context
from spddo.subs.model import Base
import pytest


@pytest.fixture(scope="module")
def context():
    engine = db_connection.register_db("sqlite:///", [Base])
    db_connection._session_.configure(twophase=False)
    orm_utils.create_all(Base, engine)
    return Context(-1, -1, None)
