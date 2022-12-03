# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def error_to_obj(msg):
    if type(msg) is str:
        return {"msg": msg}
    return msg or {"msg": ""}
