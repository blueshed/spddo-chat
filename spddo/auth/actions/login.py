from spddo.auth import model
from sqlalchemy.orm import joinedload
from spddo.auth.actions.validate_token import gen_access_token
from tornado.escape import url_escape


def sub_to_json(sub):
    return sub.service.cookie_url.format(
        url_escape(
            gen_access_token(sub.service.id, sub.user_id)))


def login(context: 'micro-context', email: str, password: str) -> dict:
    ''' returns a list of services to ask for cookies '''
    with context.session as session:
        user = session.query(model.User).\
            filter(model.User.email == email,
                   model.User.password == password).\
            first()
        if user is None:
            raise Exception(
                "<strong>Failed</strong> Email or password incorrect!")
        subscriptions = session.query(model.Subscription).\
            filter(model.Subscription.user == user).\
            options(joinedload(model.Subscription.service))
        result = {
            "services": [{
                            'name': sub.service.name,
                            'url': sub_to_json(sub)
                          } for sub in subscriptions],
        }
        return result
