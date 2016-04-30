from spddo.micro.func import model
from blueshed.micro.orm.orm_utils import serialize


def filter_images(context: 'micro-context', term: str='',
                  offset: int=0, limit: int=10) -> list:
    with context.session as session:
        term = "{}%".format(term)
        images = session.query(model.Image).\
            filter(model.Image.name.like(term)).\
            order_by(model.Image.name).\
            offset(offset).\
            limit(limit)

        return [serialize(image) for image in images]
