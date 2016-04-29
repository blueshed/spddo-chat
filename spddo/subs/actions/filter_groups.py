from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize


def filter_groups(context: 'micro-context', term: str='',
                  offset: int=0, limit: int=10, id: int=None):
    with context.session as session:
        if id:
            group = session.query(model.Group).get(id)
            result = serialize(group) if group else None
            return result
        term = "{}%".format(term)
        groups = session.query(model.Group).\
            filter(model.Group.name.like(term)).\
            order_by(model.Group.name).\
            offset(offset).\
            limit(limit)

        return [serialize(group) for group in groups]
