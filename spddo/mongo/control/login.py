from tornado import gen
from tornado.web import HTTPError


@gen.coroutine
def login(context: 'micro-context', email: str, password: str) -> dict:
    ''' returns a user object on success '''
    db = context.motor
    document = yield db.users_collection.find_one({'email': email})
    if document is None:
        raise HTTPError(
            401,
            "<strong>Failed</strong> Email or password incorrect!")
    user = {
        "id": str(document['_id']),
        "email": document['email']
    }
    context.set_cookie("current_user", user)
    return user
