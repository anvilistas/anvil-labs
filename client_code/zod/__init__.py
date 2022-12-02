# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from ._types import stringType as string

_version__ = "0.0.1"

if __name__ == "__main__":
    x = string().min(4)
    assert x.parse("foobarbaz") == "foobarbaz"
    assert x.safe_parse("foobarbaz").success
    assert not x.safe_parse("foo").success
