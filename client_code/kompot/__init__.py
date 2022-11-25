# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from ._batcher import batch_call  # noqa F401
from ._register import register  # noqa F401
from ._rpc import call, call_async, call_s, callable  # noqa F401
from ._serialize import preserve, reconstruct, serialize  # noqa F401
from ._persist import (  # noqa F401
    LinkedAttribute,
    RowBackedStore,
    persisted_class,
    row_backed_class,
)

__version__ = "0.0.1"

# from Wikipedia:
# In 1885, Lucyna Ćwierczakiewiczowa wrote in a recipe book that
# kompot preserved fruit so well it seemed fresh
