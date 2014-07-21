import re
import json
import datetime
from dateutil import parser

__author__ = 'sbermudel'

DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
DEFAULT_ARGUMENT = "datetime_format"


class JsonClitellumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(JsonClitellumEncoder, self).default(obj)


def loads(s, **kwargs):
    format = kwargs.pop(DEFAULT_ARGUMENT, None) or DEFAULT_DATE_FORMAT
    source = json.loads(s, **kwargs)

    return iteritems(source, format)


def iteritems(source, format):
    for k, v in source.items():
        if isinstance(v, dict):
            iteritems(v, format)
        elif isinstance(v, str):
            match = re.search('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])?T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)??(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$', v)
            if not match is None:
                source[k] = parser.parse(v)
                pass
            else:
                try:
                    source[k] = datetime.datetime.strptime(v, format)
                except:
                    pass

    return source


def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=JsonClitellumEncoder, indent=None, separators=None,
          encoding='utf-8', default=None, **kw):
    return json.dumps(obj, skipkeys, ensure_ascii, check_circular,
                      allow_nan, cls, indent, separators,
                      encoding, default, **kw)



