from tornado import gen
import logging
from spddo.mongo.control.signals import ALLOCATION_ADDED, ALLOCATION_CHANGED


@gen.coroutine
def allocate(context: 'micro_context', allocation: dict) -> dict:
    context.authenticated()
    db = context.motor
    result = yield db.allocation_collection.update({"id": allocation["id"]},
                                                   allocation,
                                                   upsert=True)
    logging.info(result, allocation)
    if result.get('ok') is not 1:
        raise Exception(result)

    if result.get('updatedExisting') is True:
        context.broadcast(ALLOCATION_CHANGED, allocation)
    else:
        allocation["_id"] = result.get('upserted')
        context.broadcast(ALLOCATION_ADDED, allocation)
    return str(result)
