# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil import is_server_side

from .. import batched
from ._rpc import call, call_s, callable

__version__ = "0.0.1"

PRIVATE_NAME = "kompot.private.batch_call"

if is_server_side():
    callable(PRIVATE_NAME)(batched._do_batch_call)


class batch_call(batched.batch_call):
    @staticmethod
    def server_call(*args, **kws):
        return call(PRIVATE_NAME, *args, **kws)

    @staticmethod
    def server_call_s(*args, **kws):
        return call_s(PRIVATE_NAME, *args, **kws)


def batch_call_s():
    return batch_call(silent=True)
