from blueshed.micro.utils.orm_utils import serialize
from blueshed.tests.actions import model


def save_group(context: 'micro-context',
               name: str,
               id: int=None):
    with context.session as session:
        if id:
            group = session.query(model.Group).get(id)
            group.name = name
            signal = "group-changed"
        else:
            group = model.Group(name=name)
            signal = "group-added"
            session.add(group)
        session.commit()
        result = serialize(group)
        context.broadcast(signal, result)
        return result
