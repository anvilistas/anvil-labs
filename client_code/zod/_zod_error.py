# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

import json

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


class FieldErrors(util.DictLike):
    def __init__(self):
        self._errors = []

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            return FieldErrors()

    def __repr__(self):
        if len(self.__dict__) > 1 and not self._errors:
            d = dict(self)
            d.pop("_errors")
            return repr(d)

        return repr(self.__dict__)


class ZodError(Exception):
    def __init__(self, issues):
        self.issues = issues
        Exception.__init__(self, json.dumps(self.issues, indent=2))

    def format(self):
        def mapper(issue):
            return issue.get("msg", "unknown")

        field_errors = FieldErrors()

        def process_error(error: ZodError):
            for issue in error.issues:
                code = issue.get("code", None)
                path = issue["path"]

                if code == ZodIssueCode.invalid_union:
                    for issue in issue["union_issues"]:
                        process_error(ZodError(issue))
                elif not path:
                    field_errors._errors.append(mapper(issue))

                else:
                    curr = field_errors
                    i = 0
                    while i < len(path):
                        el = path[i]
                        terminal = i == len(path) - 1
                        curr[el] = curr.get(el) or FieldErrors()
                        if terminal:
                            curr[el]._errors.append(mapper(issue))

                        curr = curr[el]
                        i += 1

        process_error(self)
        return field_errors
