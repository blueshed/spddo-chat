from blueshed.micro.orm.db_connection import register_db
from blueshed.micro.orm import db_connection
import spddo.subs.model as subs_model
import spddo.auth.model as auth_model


register_db(
    "mysql+pymysql://root:root@localhost:8889/subs", [subs_model.Base])
register_db(
    "mysql+pymysql://root:root@localhost:8889/auth", [auth_model.Base])


def test_create():
    with db_connection.session() as session:
        subs_user = subs_model.User(
            name="foo", email="foo@bar.com", password="password")
        session.add(subs_user)
        auth_user = auth_model.User(
            name="bar", email="bar@bar.com", password="password")
        session.add(auth_user)
        session.commit()


def test_fetch():
    with db_connection.session() as session:
        subs_user = session.query(
            subs_model.User).filter_by(name="foo").first()
        assert subs_user.email == "foo@bar.com"
        auth_user = session.query(
            auth_model.User).filter_by(name="bar").first()
        assert auth_user.email == "bar@bar.com"


def test_delete():
    with db_connection.session() as session:
        session.query(
            subs_model.User).filter_by(name="foo").delete()
        session.query(
            auth_model.User).filter_by(name="bar").delete()
        session.commit()
