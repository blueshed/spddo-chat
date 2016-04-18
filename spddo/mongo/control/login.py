from tornado import gen

class AuthenticationException(Exception):
    pass

@gen.coroutine
def login(context:'micro-context', email:str, password:str) -> dict:
    ''' returns a user object on success '''
    db = context.motor
    document = yield db.users_collection.find_one({'email': email})
    if document is None:
        raise AuthenticationException("<strong>Failed</strong> Email or password incorrect!")
    user = document.to_dict()
    context.set_cookie("current_user", user)
    return user
