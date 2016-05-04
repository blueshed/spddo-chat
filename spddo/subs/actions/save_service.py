from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize


def save_service(context: 'micro_context',
                 name: str,
                 description: str,
                 cost: float,
                 duration: int=None,
                 token_url: str=None,
                 cors: str=None,
                 id: int=None):
    with context.session as session:
        if id:
            service = session.query(model.Service).get(id)
            service.name = name
            service.description = description
            service.cost = cost
            service.duration = duration
            if token_url:
                service.token_url = token_url
            if cors:
                service.cors = cors
            signal = "service-changed"
        else:
            service = model.Service(name=name,
                                    description=description,
                                    cost=cost,
                                    duration=duration,
                                    token_url=token_url,
                                    cors=cors)
            signal = "service-added"
            session.add(service)
        session.commit()
        result = serialize(service)
        context.broadcast(signal, result)
        return result
