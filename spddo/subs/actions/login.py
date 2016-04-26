from spddo.subs import model
from tornado.web import HTTPError


def login(context: 'micro-context', email: str, password: str) -> dict:
    ''' returns a user object on success '''
    with context.session as session:
        person = session.query(model.User).\
            filter(model.User.email == email,
                   model.User.password == password).\
            first()
        if person is None:
            raise HTTPError(
                401,
                "<strong>Failed</strong> Email or password incorrect!")
        user = {
            "id": person.id,
            "email": person.email,
            "name": person.name
        }
        context.set_cookie("current_user", user)
        return user
