# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"


def get_atom_prop_repr(atom, prop):
    tp_name = type(atom).__name__
    if isinstance(atom, dict):
        return f"{tp_name}[{prop!r}]"
    return f"{tp_name}.{prop}"


class _A:
    def foo(self):
        pass


MethodType = type(_A().foo)
