from tornado import gen


@gen.coroutine
def allocations(context:'micro-context', from_date:int, to_date: int) -> list:
    db = context.motor
    cursor = db.allocation_collection.find({"$or":[
                                              {"$and":[{"from_date":{"$lt": to_date}},{"from_date":{"$gte": from_date}}]},
                                              {"$and":[{"to_date":{"$lte": to_date}},{"from_date":{"$gt": from_date}}]},
                                              {"$and":[{"from_date":{"$lte": from_date}},{"to_date":{"$gte": to_date}}]}
                                            ]
                                      }).sort("from_date")
    result = []
    for document in (yield cursor.to_list(length=100)):
        result.append(dict(document))
    return result
