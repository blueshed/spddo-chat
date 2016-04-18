from spddo.micro.func import model
from blueshed.micro.utils.pool import pool

@pool
def login(context:'micro-context', email:str, password:str) -> dict:
    ''' returns a user object on success '''
    with context.session as session:
        person = session.query(model.Person).\
                         filter(model.Person.email==email,
                                model.Person.password==password).\
                         first()
        if person is None:
            raise Exception("<strong>Failed</strong> Email or password incorrect!")
        user = {
            "id": person.id,
            "email": person.email
        } 
        context.set_cookie("current_user", user)
        return user