from tornado import gen


@gen.coroutine
def save_asset(context:'micro-context', asset:dict) -> dict:
        db = context.motor
        result = yield db.asset_collection.update({"id": asset["id"]},
                                                  asset,
                                                  upsert=True)
        
        if result.get('ok') is not 1:
            raise Exception(result)
        
        if result.get('updatedExisting') is True:
            context.broadcast("asset-changed", asset)
        else:    
            asset["_id"] = result.get('upserted')
            context.broadcast("asset-added", asset)
        return str(result)

