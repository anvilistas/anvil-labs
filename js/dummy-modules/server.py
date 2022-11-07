# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
# flake8: noqa

__version__ = "0.0.1"


class SerializationError(Exception):
    pass


def get_app_origin():
    return self.anvilAppOrigin


def get_api_origin():
    return get_app_origin() + "/_/api"


def call(*args, **kws):
    from anvil_labs.kompot import preserve, reconstruct, serialize

    name, *args = args

    rv = self.fetch(
        get_api_origin() + f"/anvil_labs_private_call?name={name}",
        {
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "body": self.JSON.stringify(preserve([args, kws])),
        },
    )

    result, error = rv.json()
    if error:
        raise Exception(error)
    return reconstruct(dict(result))


def portable_class(*args, **kws):
    from anvil_labs.kompot import register

    return register(*args)
