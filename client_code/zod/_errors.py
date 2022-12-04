# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .helpers import util
from .helpers.parse_util import DictLike

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


class FieldErrors(DictLike):
    def __init__(self):
        self._errors = []


class ZodError(Exception):
    def __init__(self, issues):
        self.issues = issues
        msg = ""
        Exception.__init__(self, msg)

    def format(self):
        def mapper(issue):
            return issue.get("msg", "")

        field_errors = FieldErrors()

        def process_error(error: ZodError):
            for issue in error.issues:
                code = issue.get("code", None)
                path = issue["path"]

                if code == ZodIssueCode.invalid_union:
                    for error in issue["union_errors"]:
                        process_error(error)
                elif not path:
                    field_errors._errors.append(mapper(issue))

                else:
                    curr = field_errors
                    i = 0
                    while i < len(path):
                        el = path[i]
                        terminal = i == len(path) - 1

                        curr[el] = curr[el] or FieldErrors()
                        if terminal:
                            curr[el]._errors.append(mapper(issue))

                        curr = curr[el]
                        i += 1

        process_error(self)
        return field_errors
