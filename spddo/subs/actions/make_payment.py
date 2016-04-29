from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize
from spddo.subs.actions.subscribe import sub_to_json
from spddo.subs.model import Payment
import datetime


def make_payment(context: 'micro-context',
                 user_id: int=None,
                 group_id: int=None):
    if group_id is not None and user_id is not None:
        raise Exception("only a user or a group can pay for subscription")

    with context.session as session:
        subscriptions = session.query(model.Subscription).\
            filter(model.Subscription.from_date.is_(None))
        if user_id is not None:
            subscriptions = subscriptions.filter(
                model.Subscription.user_id == user_id)
        elif group_id is not None:
            subscriptions = subscriptions.filter(
                model.Subscription.group_id == group_id)
        subscriptions = list(subscriptions)
        if not subscriptions:
            raise Exception("Nothing to pay")

        cost = sum([row.cost for row in subscriptions])
        payee = Payment.PAYEE[0] if user_id is not None else Payment.PAYEE[1]
        payment = model.Payment(amount=cost,
                                payee=payee,
                                date=datetime.date.today())
        session.add(payment)
        for subscription in subscriptions:
            subscription.payment = payment
            subscription.from_date = payment.date
            if subscription.service.duration:
                days = subscription.service.duration
                to_date = payment.date + datetime.timedelta(days=days)
                subscription.to_date = to_date
        session.commit()
        for subscription in subscriptions:
            message = sub_to_json(subscription)
            context.broadcast('subscription-active', message)
        return serialize(payment)
