import datetime
from blueshed.micro.utils.utils import gen_token
from tornado.ioloop import IOLoop
import functools
from spddo.auth import model


tokens = []


def remove_timeout(timeout):
    ''' callback to timeout token '''
    global tokens
    tokens = [t for t in tokens if t != timeout]


def remove_token(token, service_id):
    ''' searches tokens for values and return user_id if found '''
    global tokens
    timeout = None
    for timeout in tokens:
        t, s_id, u_id, _ = timeout
        if t == token and s_id == service_id:
            break
    if timeout:
        tokens.remove(timeout)
        return u_id
    raise Exception("token or service token invalid")


def gen_access_token(service_id, user_id):
    ''' save a timeout and return token '''
    global tokens
    token = gen_token()
    timeout = (token, service_id, user_id, datetime.datetime.now())
    tokens.append(timeout)

    # set a timeout in ioloop to remove old tokens
    IOLoop.current().add_timeout(datetime.timedelta(seconds=3),
                                 functools.partial(remove_timeout,
                                                   timeout))
    return token


def validate_token(context: 'micro_context',
                   token: str, service_token: str) -> dict:
    ''' returns a user dict if token is valid '''
    with context.session as session:
        service = session.query(model.Service).\
                          filter(model.Service.token == service_token).\
                          first()
        if service is None:
            raise Exception("service not found")
        user_id = remove_token(token, service.id)
        user = session.query(model.User).get(user_id)
        if user is None:
            raise Exception("No such user")
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
