# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas


def error_to_obj(msg):
    if type(msg) is str:
        return {"msg": msg}
    return msg or {"msg": ""}
