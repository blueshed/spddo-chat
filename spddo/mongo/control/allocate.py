from tornado import gen
import logging


@gen.coroutine
def allocate(context:'micro-context', allocation:dict) -> dict:
        db = context.motor
        result = yield db.allocation_collection.update({"id": allocation["id"]},
                                                       allocation,
                                                       upsert=True)
        logging.info(result, allocation)
        if result.get('ok') is not 1:
            raise Exception(result)
        
        if result.get('updatedExisting') is True:
            context.broadcast("allocation-changed", allocation)
        else:    
            allocation["_id"] = result.get('upserted')
            context.broadcast("allocation-added", allocation)
        return result