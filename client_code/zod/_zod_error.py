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
        # "invalid_union_discriminator",
        "invalid_enum_value",
        "unrecognized_keys",
        # "invalid_arguments",
        # "invalid_return_type",
        "invalid_date",
        "invalid_string",
        "too_small",
        "too_big",
        # "invalid_intersection_types",
        # "not_multiple_of",
        # "not_finite",
    ],
)


class FieldErrors(util.DictLike):
    __slots__ = ["_errors", "__dict__"]

    def __init__(self):
        self._errors = []

    def __repr__(self):
        if self.__dict__ and not self._errors:
            return repr(self.__dict__)
        return repr({"_errors": self._errors, **self.__dict__})


def _join_path(path):
    return "".join(f"[{p!r}]" for p in path)


def _join_messages(issue):
    path = issue["path"]
    message = issue.get("message", "unknown")
    if path:
        return f"{message} at {_join_path(path)}"
    else:
        return message


def _mapper(issue):
    return issue.get("message", "unknown")


class ZodError(Exception):
    def __init__(self, issues):
        self.issues = issues
        self._formatted = None
        self.message = "; ".join(map(_join_messages, issues))
        Exception.__init__(self, self.message)

    def format(self, mapper=_mapper):
        if self._formatted:
            return self._formatted

        self._formatted = field_errors = FieldErrors()

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

    def errors(self, path=None, mapper=_mapper):
        "returns a list of error messages at the specified path"
        formatted = self.format(mapper)
        if path is None:
            return formatted._errors
        if type(path) is not list:
            path = [path]

        for p in path:
            formatted = formatted.get(p) or FieldErrors()
        return formatted._errors
