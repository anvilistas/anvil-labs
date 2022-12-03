# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from .slotum import Slotum

__version__ = "0.0.1"

VALID = "valid"
DIRTY = "dirty"
ABORTED = "aborted"
MISSING = object()  # TODO


class Common(Slotum):
    __slots__ = ["issues", "context_error_map"]


class ParseContext(Slotum):
    __slots__ = ["common", "path", "schema_error_map", "parent", "data", "parsed_type"]


class ParseInput(Slotum):
    __slots__ = ["data", "path", "parent"]


class ParseReturn(Slotum):
    __slots__ = ["status", "value"]


class ParseResult(Slotum):
    __slots__ = ["success", "data", "error"]


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


def make_issue(issue_data, data, path, error_maps):
    full_path = [*path, *issue_data.get("path", [])]
    # full_issue = {**issue_data, "path": full_path}
    error_msg = ""
    # const maps = errorMaps
    #   .filter((m) => !!m)
    #   .slice()
    #   .reverse() as ZodErrorMap[];
    # for (const map of maps) {
    #   errormsg = map(fullIssue, { data, defaultError: errormsg }).msg;
    # }
    return {**issue_data, "path": full_path, "msg": issue_data.get("msg", error_msg)}


def add_issue_to_context(ctx: ParseContext, **issue_data):
    issue = make_issue(
        issue_data=issue_data,
        data=ctx.data,
        path=ctx.path,
        error_maps=[
            # ctx.common.contextual_error_map,
            # ctx.schema_error_map,
            # get_error_map(),
            # default_error_map()
        ],  # filter(x => !!x)
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
