# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from . import utils

_version__ = "0.0.1"

VALID = "valid"
DIRTY = "dirty"
ABORTED = "aborted"
MISSING = object()


class ZodTypeDef(utils.Slotum):
    __slots__ = ["error_map", "description"]


class CommonContext(utils.Slotum):
    __slots__ = ["issues", "context_error_map"]


class ParseContext(utils.Slotum):
    __slots__ = ["common", "path", "schema_error_map", "parent", "data", "parsed_type"]


class ParseInput(utils.Slotum):
    __slots__ = ["data", "path", "parent"]


class ParseReturn(utils.Slotum):
    __slots__ = ["status", "value"]


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


INVALID = ParseStatus(ABORTED)


class Result(utils.Slotum):
    __slots__ = ["success", "data", "error"]


class ZodError(Exception):
    pass  # TODO


def is_valid(x):
    return x.status == VALID


# enum class
ZodParseType = utils.enum("ZodParseType", ["str", "unknown"])
ZodIssueCode = utils.enum(
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


def get_parsed_type(data):
    tp = type(data)
    if tp is str:
        return ZodParseType.str
    else:
        return ZodParseType.unknown


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


def handle_result(ctx, result):
    if is_valid(result):
        return Result(success=True, data=result.value, error=None)
    else:
        if not ctx.common.issues:
            raise Exception("Validation failed but no issues detected")
        error = ZodError(ctx.common.issues)
        return Result(success=False, data=None, error=error)


class ZodType:
    def __init__(self, _def):
        self._def = _def

    @property
    def description(self):
        return self._def["description"]

    def _parse(self, input):
        raise NotImplementedError("should be implemented by subclass")

    def _get_type(self, input):
        return get_parsed_type(input.data)

    def _get_or_return_ctx(self, input: ParseInput, ctx=None):
        return ctx or ParseContext(
            common=input.parent.common,
            data=input.data,
            parsed_type=get_parsed_type(input.data),
            schema_error_map=self._def.get("error_map"),
            path=input.path,
            parent=input.parent,
        )

    def _process_input_params(self, input: ParseInput):
        return ParseStatus(), self._get_or_return_ctx(input)

    _parse_sync = _parse

    def parse(self, data, **params):
        result = self.safe_parse(data, **params)
        if result.success:
            return result.data
        raise result.error

    def safe_parse(self, data, **params):
        ctx = ParseContext(
            common=CommonContext(issues=[], context_error_map=params.get("error_map")),
            path=params.get("path", []),
            schema_error_map=self._def.get("error_map"),
            parent=None,
            data=data,
            parsed_type=get_parsed_type(data),
        )
        input = ParseInput(data, path=ctx.path, parent=ctx)
        result = self._parse(input)
        return handle_result(ctx, result)


class ZodString(ZodType):
    def _parse(self, input: ParseInput):
        parsed_type = self._get_type(input)

        if parsed_type is not ZodParseType.str:
            ctx = self._get_or_return_ctx(input)
            add_issue_to_context(
                ctx,
                code=ZodIssueCode.invalid_type,
                expected=ZodParseType.str,
                received=ctx.parsed_type,
            )
            return INVALID

        status = ParseStatus()
        ctx = None
        for check in self._def["checks"]:
            if check["kind"] == "min":
                if len(input.data) < check["value"]:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_small,
                        minimum=check["value"],
                        type="str",
                        inclusive=True,
                        msg=check["msg"],
                    )
                    status.dirty()
            else:
                assert False

        return ParseReturn(status=status.value, value=input.data)

    def _add_check(self, **check):
        return ZodString({**self._def, "checks": [*self._def["checks"], check]})

    def min(self, min_length: int, msg=""):
        return self._add_check(kind="min", value=min_length, msg=msg)

    @classmethod
    def create(cls, **params):
        _def = {"checks": [], "type_name": cls.__name__, **params}
        return cls(_def)


stringType = ZodString.create
