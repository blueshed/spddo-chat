from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import and_
from tornado.escape import url_escape
from tornado.web import HTTPError
from spddo.auth import model
from spddo.auth.actions.validate_token import gen_access_token
import logging


def sub_to_json(sub):
    return sub.service.cookie_url.format(
        url_escape(
            gen_access_token(sub.service.id, sub.user_id)))


def login(context: 'micro_context', email: str, password: str) -> dict:
    ''' returns a list of services to ask for cookies '''
    logging.info("login: %s", email)
    with context.session as session:
        user = session.query(model.User).\
            filter(and_(model.User.email == email,
                        model.User.password == password)).\
            first()
        if user is None:
            raise HTTPError(
                401,
                "<strong>Failed</strong> Email or password incorrect!")
        subscriptions = session.query(model.Subscription).\
            filter(model.Subscription.user == user).\
            options(joinedload(model.Subscription.service))
        if subscriptions.count() is 0:
            raise Exception("You have no subscriptions!")
        result = {
            "services": [{
                'name': sub.service.name,
                'url': sub_to_json(sub)
            } for sub in subscriptions],
        }
        return result
