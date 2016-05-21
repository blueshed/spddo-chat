from tornado import gen
from spddo.mongo.control.signals import ASSET_CHANGED, ASSET_ADDED


@gen.coroutine
def save_asset(context: 'micro_context', asset: dict) -> dict:
    context.authenticated()
    db = context.motor
    assert asset.get("name")
    result = yield db.asset_collection.update({"id": asset["id"]},
                                              asset,
                                              upsert=True)

    if result.get('ok') is not 1:
        raise Exception(result)

    if result.get('updatedExisting') is True:
        context.broadcast(ASSET_CHANGED, asset)
    else:
        asset["_id"] = result.get('upserted')
        context.broadcast(ASSET_ADDED, asset)
    return str(result)
