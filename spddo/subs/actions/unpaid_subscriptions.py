from spddo.subs import model
from sqlalchemy.orm import subqueryload
from spddo.subs.actions.subscribe import sub_to_json


def unpaid_subscriptions(context: 'micro_context',
                         user_id: int=None,
                         group_id: int=None):
    with context.session as session:
        result = session.query(model.Subscription).\
            filter(model.Subscription.from_date.is_(None))
        if user_id is not None:
            result = result.filter(model.Subscription.user_id == user_id)
        if group_id is not None:
            result = result.filter(model.Subscription.group_id == group_id)
        result = result.options(subqueryload(model.Subscription.user))
        result = result.options(subqueryload(model.Subscription.group))
        result = result.options(subqueryload(model.Subscription.service))
        return [sub_to_json(row) for row in result]
