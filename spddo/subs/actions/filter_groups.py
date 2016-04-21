from spddo.subs import model
from blueshed.micro.utils.orm_utils import serialize


def filter_groups(context: 'micro-context', term='', offset=0, limit=10, id=None):
    with context.session as session:
        if id is not None:
            group = session.query(model.Group).get(id)
            result = serialize(group)
            return result
        term = "{}%".format(term)
        groups = session.query(model.Group).\
            filter(model.Group.name.like(term))

        return [serialize(group) for group in groups]
