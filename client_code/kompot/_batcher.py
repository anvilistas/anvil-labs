# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from anvil import is_server_side

from .. import batcher
from ._rpc import _registered, call, call_s, callable

__version__ = "0.0.1"

PRIVATE_NAME = "kompot.private.batch_call"

if is_server_side():
    do_batch_call = callable(PRIVATE_NAME)(
        lambda call_sigs: batcher.do_batch_call(call_sigs, _registered)
    )


class batch_call(batcher.batch_call):
    @staticmethod
    def server_call(*args, **kws):
        return call(*args, **kws)

    @staticmethod
    def server_call_s(*args, **kws):
        return call_s(*args, **kws)


def batch_call_s():
    return batch_call(silent=True)
