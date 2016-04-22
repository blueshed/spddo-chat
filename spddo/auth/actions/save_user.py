from spddo.auth import model
from blueshed.micro.utils.orm_utils import serialize


def save_user(context: 'micro-context',
              user_id: int,
              name: str=None,
              email: str=None,
              password: str=None):
    with context.session as session:
        user = session.query(model.User).get(user_id)
        if user:
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if password is not None:
                user.password = password
            signal = "user-changed"
        else:
            user = model.User(id=user_id,
                              name=name,
                              email=email,
                              password=password)
            signal = "user-added"
            session.add(user)
        session.commit()
        result = serialize(user)
        del result['password']
        context.broadcast(signal, result)
        return result
