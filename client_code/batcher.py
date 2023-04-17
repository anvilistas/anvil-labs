# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil.server
from anvil import is_server_side

__version__ = "0.0.1"

PRIVATE_NAME = "anvil-labs.private.batch_call"

_registered = {}


def do_batch_call(call_sigs, registered):
    rv = []
    for fn_name, args, kws in call_sigs:
        try:
            fn = registered[fn_name]
        except KeyError:
            raise anvil.server.NoServerFunctionError(
                f"No server batchable function matching '{fn_name}' has been registered"
            )
        rv.append(fn(*args, **kws))

    if len(call_sigs) > 1:
        return rv
    else:
        return rv[0]


if is_server_side():
    anvil.server.callable(PRIVATE_NAME)(
        lambda call_sigs: do_batch_call(call_sigs, _registered)
    )


def _register(fn, name=None):
    if name is None:
        name = fn.__name__
    _registered[name] = fn
    return fn


def batchable(fn):
    return _register(fn)


def callable(fn_or_name=None, require_user=None):
    if fn_or_name is None or isinstance(fn_or_name, str):
        _callable_decorator = anvil.server.callable(
            fn_or_name, require_user=require_user
        )
        return lambda fn: _callable_decorator(_register(fn, fn_or_name))
    return anvil.server.callable(_register(fn_or_name))


class batch_call:
    @staticmethod
    def server_call(*args, **kws):
        return anvil.server.call(*args, **kws)

    @staticmethod
    def server_call_s(*args, **kws):
        return anvil.server.call_s(*args, **kws)

    def __init__(self, *, silent=False):
        self._result = None
        self._silent = silent
        self._sigs = []
        self._enter = False
        self._exit = False

    def call(self, fn_name, *args, **kws):
        self._sigs.append([fn_name, args, kws])

    @property
    def result(self):
        if not self._exit:
            raise RuntimeError(
                "accessing result inside batch_call context is not allowed"
            )
        return self._result

    def __enter__(self):
        if self._enter:
            raise RuntimeError("cannot re-execute a batched call")
        self._enter = True
        return self

    def __exit__(self, exc_type, *exc_args):
        self._exit = True
        sigs, self._sigs = self._sigs, []

        if exc_type:
            # an exception was raised inside the context
            return

        call_method = self.server_call_s if self._silent else self.server_call

        if sigs:
            self._result = call_method(PRIVATE_NAME, sigs)


def batch_call_s():
    return batch_call(silent=True)
