from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize


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
        if not user_id:
            raise Exception("No such user")
        service = session.query(model.Service).get(service_id)
        if service is None:
            raise Exception("No such service")
        subscription = model.Subscription(user_id=user_id,
                                          group_id=group_id,
                                          service=service,
                                          cost=service.cost)
        session.add(subscription)
        session.commit()
        result = sub_to_json(subscription)
        context.broadcast('subscription-added', result)
        return result
