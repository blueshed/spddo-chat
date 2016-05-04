from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.orm import subqueryload
from blueshed.micro.utils.date_utils import parse_date
from spddo.subs.actions.subscribe import sub_to_json
from spddo.subs import model
import datetime


def active_subscriptions_for(session, user_id=None, group_id=None,
                             on_date=None, loaded=True):
    if on_date is None:
        on_date = datetime.date.today()
    else:
        on_date = parse_date(on_date)
    result = session.query(model.Subscription).\
        filter(and_(model.Subscription.from_date <= on_date,
                    or_(model.Subscription.to_date > on_date,
                        model.Subscription.to_date.is_(None))))
    if user_id is not None:
        result = result.filter(model.Subscription.user_id == user_id)
    if group_id is not None:
        result = result.filter(model.Subscription.group_id == group_id)

    if loaded is True:
        result = result.options(subqueryload(model.Subscription.user))
        result = result.options(subqueryload(model.Subscription.group))
        result = result.options(subqueryload(model.Subscription.service))
    return result


def active_subscriptions(context: 'micro_context',
                         user_id: int=None,
                         group_id: int=None,
                         on_date: str=None):
    with context.session as session:
        result = active_subscriptions_for(session, user_id, group_id, on_date)
        return [sub_to_json(row) for row in result]
