from tornado import gen


@gen.coroutine
def add_asset(context:'micro-context', asset:dict) -> dict:
        db = context.motor
        _id = yield db.asset_collection.insert(asset)
        asset["_id"] = _id
        context.broadcast("asset-added", asset)
