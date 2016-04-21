from spddo.subs import model
from blueshed.micro.utils.orm_utils import serialize


def save_service(context: 'micro-context',
                 name: str,
                 description: str,
                 cost: float,
                 duration: int=None,
                 id: int=None):
    with context.session as session:
        if id:
            service = session.query(model.Service).get(id)
            service.name = name
            service.description = description
            service.cost = cost
            service.duration = duration
            signal = "service-changed"
        else:
            service = model.Service(name=name,
                                    description=description,
                                    cost=cost,
                                    duration=duration)
            signal = "service-added"
            session.add(service)
        session.commit()
        result = serialize(service)
        context.broadcast(signal, result)
        return result
