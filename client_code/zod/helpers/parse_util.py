# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"

from ..errors import get_error_map
from ..locales.en import error_map as default_error_map
from .util import DictLike

VALID = "valid"
DIRTY = "dirty"
ABORTED = "aborted"
MISSING = object()  # TODO


class Common(DictLike):
    def __init__(self, issues, contextual_error_map):
        self.issues = issues
        self.contextual_error_map = contextual_error_map


class ParseContext(DictLike):
    def __init__(
        self, common: Common, path, schema_error_map, parent, data, parsed_type
    ):
        self.common = common
        self.path = path
        self.schema_error_map = schema_error_map
        self.parent = parent
        self.data = data
        self.parsed_type = parsed_type


class ParseInput(DictLike):
    def __init__(self, data, path, parent):
        self.data = data
        self.path = path
        self.parent = parent


class ParseReturn(DictLike):
    def __init__(self, status, value):
        self.status = status
        self.value = value


class ParseResult(DictLike):
    def __init__(self, success, data, error):
        self.success = success
        self.data = data
        self.error = error


class ParseStatus:
    def __init__(self, value=VALID):
        self.value = value

    def dirty(self):
        if self.value == VALID:
            self.value = DIRTY

    def abort(self):
        if self.value != ABORTED:
            self.value = ABORTED

    @staticmethod
    def merge_list(status, results):
        list_value = []
        for s in results:
            if s.status == ABORTED:
                return INVALID
            if s.status == DIRTY:
                status.dirty()
            list_value.append(s.value)

        return ParseReturn(status.value, list_value)

    @staticmethod
    def merge_dict(status, pairs):
        final = {}
        for key, value, always_set in pairs:
            if key.status == ABORTED or value.status == ABORTED:
                return INVALID
            if key.status == DIRTY or value.status == DIRTY:
                status.dirty()

            if value.value is not MISSING or always_set:
                final[key.value] = value.value

        return ParseReturn(status.value, final)


INVALID = ParseReturn(ABORTED, None)


class ErrorMapContext(DictLike):
    def __init__(self, data, default_error):
        self.data = data
        self.default_error = default_error


def make_issue(issue_data, data, path, error_maps):
    full_path = [*path, *issue_data.get("path", [])]
    full_issue = {**issue_data, "path": full_path}
    error_msg = ""
    maps = reversed(list(filter(None, error_maps)))
    for map in maps:
        error_msg = map(
            full_issue, ErrorMapContext(data=data, default_error=error_msg)
        )["msg"]
    return {**issue_data, "path": full_path, "msg": issue_data.get("msg") or error_msg}


def add_issue_to_context(ctx: ParseContext, **issue_data):
    issue = make_issue(
        issue_data=issue_data,
        data=ctx.data,
        path=ctx.path,
        error_maps=[
            m
            for m in (
                ctx.common.contextual_error_map,
                ctx.schema_error_map,
                get_error_map(),
                default_error_map,
            )
            if m
        ],
    )
    ctx.common.issues.append(issue)


def is_valid(x):
    return x.status == VALID


def is_aborted(x):
    return x.status == ABORTED


def is_dirty(x):
    return x.status == DIRTY


def OK(value):
    return ParseReturn(status=VALID, value=value)
