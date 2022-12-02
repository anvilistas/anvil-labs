# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .helpers import util

__version__ = "0.0.1"

ZodIssueCode = util.enum(
    "ZodIssueCode",
    [
        "invalid_type",
        "invalid_literal",
        "custom",
        "invalid_union",
        "invalid_union_discriminator",
        "invalid_enum_value",
        "unrecognized_keys",
        "invalid_arguments",
        "invalid_return_type",
        "invalid_date",
        "invalid_string",
        "too_small",
        "too_big",
        "invalid_intersection_types",
        "not_multiple_of",
        "not_finite",
    ],
)


class ZodError(Exception):
    def __init__(self, issues):
        self.issues = issues
