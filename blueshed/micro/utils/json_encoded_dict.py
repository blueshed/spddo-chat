from sqlalchemy.sql.sqltypes import Text
from sqlalchemy.dialects.mysql.base import MEDIUMTEXT
from sqlalchemy.types import TypeDecorator
import json


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict()

    """

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MySQLMediumJSONEncodedDict(JSONEncodedDict):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        MySQLMediumJSONEncodedDict()

    """

    impl = MEDIUMTEXT
