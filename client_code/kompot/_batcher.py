# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil.server
from anvil import is_server_side

from ._rpc import _registered, call, call_s, callable

__version__ = "0.0.1"

PRIVATE_NAME = "kompot.private.batch_call"


def do_batch_call(call_sigs):
    rv = []
    for fn_name, args, kws in call_sigs:
        try:
            fn = _registered[fn_name]
        except KeyError:
            raise anvil.server.NoServerFunctionError(
                f"No server function matching '{fn_name}' has been registered with kompot"
            )
        rv.append(fn(*args, **kws))

    if len(call_sigs) > 1:
        return rv
    else:
        return rv[0]


if is_server_side():
    do_batch_call = callable(PRIVATE_NAME)(do_batch_call)


class batch_call:
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

        call_method = call_s if self._silent else call
        if sigs:
            self._result = call_method(PRIVATE_NAME, sigs)


def batch_call_s():
    return batch_call(silent=True)
