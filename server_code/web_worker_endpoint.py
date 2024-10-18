# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import anvil.server
from anvil_labs import kompot

__version__ = "0.0.1"


@anvil.server.http_endpoint("/anvil_labs_private_call")
def anvil_labs_private_call(name):
    args, kws = kompot.reconstruct(anvil.server.request.body_json)
    rv = [None, None]
    try:
        rv[0] = kompot.preserve(anvil.server.call(name, *args, **kws))
    except Exception as e:
        rv[1] = repr(e)

    return rv
