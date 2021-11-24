# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def get_atom_prop_repr(atom, prop):
    tp_name = type(atom).__name__
    if isinstance(atom, dict):
        return f"{tp_name}[{prop!r}]"
    return f"{tp_name}.{prop}"


# create a fake class to get a method
# we could import types.MethodType but too much overhead
class _C:
    def _m(self):
        pass


MethodType = type(_C()._m)
