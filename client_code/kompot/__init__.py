# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
from ._batcher import batch_call
from ._register import register
from ._rpc import call, call_async, call_s, callable
from ._serialize import preserve, reconstruct, serialize

__version__ = "0.0.1"

# from Wikipedia:
# In 1885, Lucyna Ćwierczakiewiczowa wrote in a recipe book that
# kompot preserved fruit so well it seemed fresh
