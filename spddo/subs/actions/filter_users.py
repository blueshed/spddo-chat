from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize
from sqlalchemy.sql.expression import or_
from spddo.subs.actions.active_subscriptions import active_subscriptions_for
from spddo.subs.actions.active_subscriptions import sub_to_json


def filter_users(context: 'micro_context', term='', offset=0, limit=10,
                 id=None):
    with context.session as session:
        if id is not None:
            user = session.query(model.User).get(id)
            result = serialize(user)
            del user['password']
            subs = active_subscriptions_for(session, user_id=id)
            result.subscriptions = [sub_to_json(o) for o in subs]
            return result
        term = "{}%".format(term)
        users = session.query(model.User).\
            filter(or_(model.User.name.like(term),
                       model.User.email.like(term)))

        result = []
        for user in users:
            item = serialize(user)
            del item['password']
            result.append(item)
        return result
