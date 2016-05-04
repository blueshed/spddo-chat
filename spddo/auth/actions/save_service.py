from spddo.auth import model
from blueshed.micro.orm.orm_utils import serialize
from blueshed.micro.utils.utils import gen_token


def save_service(context: 'micro_context',
                 service_id: int,
                 name: str,
                 cookie_url: str,
                 cors: str):
    with context.session as session:
        service = session.query(model.Service).get(service_id)
        if service:
            service.name = name
            service.cookie_url = cookie_url
            service.cors = cors
            service.token = gen_token()
            signal = "service-changed"
        else:
            service = model.Service(id=service_id,
                                    name=name,
                                    cookie_url=cookie_url,
                                    cors=cors,
                                    token=gen_token())
            signal = "service-added"
            session.add(service)
        session.commit()
        result = serialize(service)
        context.broadcast(signal, result)
        return result
