from blueshed.micro.utils.db_connection import register_db
from blueshed.micro.utils import db_connection
from spddo.subs.model import User as AuthUser
from spddo.auth.model import User as SubsUser


register_db(
    "mysql+pymysql://root:root@localhost:8889/subs", [SubsUser])
register_db(
    "mysql+pymysql://root:root@localhost:8889/auth", [AuthUser])


def test_create():
    with db_connection.session() as session:
        subs_user = SubsUser(
            name="foo", email="foo@bar.com", password="password")
        session.add(subs_user)
        auth_user = AuthUser(
            name="bar", email="bar@bar.com", password="password")
        session.add(auth_user)
        session.commit()


def test_fetch():
    with db_connection.session() as session:
        subs_user = session.query(
            SubsUser).filter_by(name="foo").first()
        assert subs_user.email == "foo@bar.com"
        auth_user = session.query(
            AuthUser).filter_by(name="bar").first()
        assert auth_user.email == "bar@bar.com"


def test_delete():
    with db_connection.session() as session:
        session.query(
            SubsUser).filter_by(name="foo").delete()
        session.query(
            AuthUser).filter_by(name="bar").delete()
        session.commit()
