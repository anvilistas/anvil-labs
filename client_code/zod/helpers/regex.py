# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"

__all__ = ["EMAIL", "UUID"]  # noqa: F822


_raw = {
    "EMAIL": r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$",
    "UUID": r"([a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12}|00000000-0000-0000-0000-000000000000)$",
    # https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
    "URL": (
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$"
    ),
}

_cache = {}


def datetime(precision=None, offset=False, **check):
    import re

    rv = _cache.get((precision, offset))
    if rv is not None is not None:
        return rv

    if precision:
        if offset:
            raw = rf"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{{{precision}}}(([+-]\\d{2}:\\d{2})|Z)$"
        else:
            raw = rf"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{{{precision}}}Z$"
    if precision == 0:
        if offset:
            raw = r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(([+-]\\d{2}:\\d{2})|Z)$"
        else:
            raw = r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(([+-]\\d{2}:\\d{2})|Z)$"
    else:
        if offset:
            raw = r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(([+-]\\d{2}:\\d{2})|Z)$"
        else:
            raw = r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?Z$"

    rv = _cache[(precision, offset)] = re.compile(raw)
    return rv


def __getattr__(self, name):
    if name not in __all__:
        raise AttributeError(name)

    # do this lazily on the client
    import re

    _cache[name] = re.compile(_raw[name], re.IGNORECASE)

    return _cache[name]


def __dir__(self):
    return __all__
