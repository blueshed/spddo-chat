from tornado import gen
import logging


@gen.coroutine
def change_allocation(context:'micro-context', allocation: dict) -> list:
    db = context.motor
    _id = allocation["_id"]
    del allocation["_id"]
    result = yield db.allocation_collection.update({'id': allocation["id"]}, 
                                                   allocation)
    logging.info(result, allocation)
    assert result.get('nModified') == 1 and result['ok'] == 1
    allocation["_id"] = _id
    context.broadcast("allocation-changed", allocation)