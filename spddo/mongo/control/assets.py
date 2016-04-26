from tornado import gen


@gen.coroutine
def assets(context: 'micro-context') -> list:
    db = context.motor
    cursor = db.asset_collection.find()
    result = []
    for document in (yield cursor.to_list(length=100)):
        result.append(dict(document))
    return result
