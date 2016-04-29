from blueshed.micro.orm import db_connection, orm_utils
from spddo.subs.actions.context import Context
import pytest


@pytest.fixture(scope="module")
def context():
    db_connection.db_init("sqlite:///")
    orm_utils.create_all(orm_utils.Base, db_connection._engine_)
    return Context(-1, -1, None)
