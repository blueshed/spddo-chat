from tornado import gen


@gen.coroutine
def allocate(context:'micro-context', allocation:dict) -> dict:
        db = context.motor
        _id = yield db.allocation_collection.insert(allocation)
        allocation["_id"] = _id
        context.broadcast("allocation-added", allocation)
