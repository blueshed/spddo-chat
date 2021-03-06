from tornado import gen
import logging
from spddo.mongo.control.signals import ALLOCATION_REMOVED


@gen.coroutine
def unallocate(context: 'micro_context', allocation_id: str) -> list:
    context.authenticated()
    db = context.motor
    result = yield db.allocation_collection.remove({'id': allocation_id})
    logging.info("%s - %s", result, allocation_id)
    assert result.get('n') == 1 and result['ok'] == 1
    context.broadcast(ALLOCATION_REMOVED, allocation_id)

    return str(result)
