from spddo.subs import model
from blueshed.micro.utils.orm_utils import serialize


def sub_to_json(o):
    result = serialize(o)
    result["user"] = o.user.name if o.user else None
    result["group"] = o.group.name if o.group else None
    result["service"] = o.service.name if o.service else None
    return result


def subscribe(context: 'micro-context',
              user_id: int,
              group_id: int,
              service_id: int):
    with context.session as session:
        service = session.query(model.Service).get(service_id)
        subscription = model.Subscription(user_id=user_id,
                                          group_id=group_id,
                                          service=service,
                                          cost=service.cost)
        session.add(subscription)
        session.commit()
        result = sub_to_json(subscription)
        context.broadcast('subscription-added', result)
        return result
