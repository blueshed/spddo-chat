from spddo.subs import model
from blueshed.micro.orm.orm_utils import serialize


def filter_services(context: 'micro-context', term='', offset=0, limit=10, id=None):
    with context.session as session:
        if id is not None:
            service = session.query(model.Service).get(id)
            result = serialize(service)
            return result
        term = "{}%".format(term)
        services = session.query(model.Service).\
            filter(model.Service.name.like(term))

        return [serialize(service) for service in services]
