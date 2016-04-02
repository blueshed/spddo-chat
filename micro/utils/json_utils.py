import json
from decimal import Decimal
import datetime
import collections


class DateTimeEncoder(json.JSONEncoder):
    """Encodes datetimes and Decimals"""

    def default(self, obj):
        try:
            if hasattr(obj, 'isoformat'):
                return obj.isoformat().replace("T", " ")
            elif isinstance(obj, datetime.date):
                return str(obj)
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj, "to_json") and isinstance(getattr(obj,
                                                                "to_json"),
                                                        collections.Callable):
                return obj.to_json()
            return json.JSONEncoder.default(self, obj)
        except:
            raise
#            return str(obj)


def loads(*args, **kwargs):
    return json.loads(*args, **kwargs)


def dumps(o, **kwargs):
    return json.dumps(o, cls=DateTimeEncoder, **kwargs)
