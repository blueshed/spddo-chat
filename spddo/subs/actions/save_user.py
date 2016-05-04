from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize


def save_user(context: 'micro_context',
              name: str=None,
              email: str=None,
              password: str=None,
              id: int=None):
    with context.session as session:
        if id:
            user = session.query(model.User).get(id)
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if password is not None:
                user.password = password
            signal = "user-changed"
        else:
            user = model.User(name=name,
                              email=email,
                              password=password)
            signal = "user-added"
            session.add(user)
        session.commit()
        result = serialize(user)
        del result['password']
        context.broadcast(signal, result)
        return result
