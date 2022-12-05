# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def err_to_obj(message):
    if type(message) is str:
        return {"message": message}
    return message or {"message": ""}
