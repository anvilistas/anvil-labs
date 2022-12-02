# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import date, datetime

from anvil import is_server_side

from ._errors import ZodError, ZodIssueCode
from .helpers import ZodParsedType, get_parsed_type, regex
from .helpers.parse_util import (
    INVALID,
    OK,
    VALID,
    Common,
    ParseContext,
    ParseInput,
    ParseResult,
    ParseReturn,
    ParseStatus,
    add_issue_to_context,
    is_valid,
)

__version__ = "0.0.1"


# enum class


def handle_result(ctx, result):
    if is_valid(result):
        return ParseResult(success=True, data=result.value, error=None)
    else:
        if not ctx.common.issues:
            raise Exception("Validation failed but no issues detected")
        error = ZodError(ctx.common.issues)
        return ParseResult(success=False, data=None, error=error)


def process_params(
    error_map=None, invalid_type_error=False, required_error=False, description=""
):
    if not any([error_map, invalid_type_error, required_error, description]):
        return {}
    if error_map and (invalid_type_error or required_error):
        raise Exception(
            'Can\'t use "invalid_type_error" or "required_error" in conjunction with custom error'
        )

    if error_map:
        return {"error_map": error_map, "description": description}

    def custom_map(iss, ctx):
        if iss["code"] != "invalid_type":
            return {"msg": ctx.default_error}
        # TODO

    return {"error_map": custom_map, "description": description}


class ZodType:
    _type = None

    @classmethod
    def _create(cls, **params):
        _def = process_params(**params)
        return cls(_def)

    def __init__(self, _def):
        self._def = _def

    @property
    def description(self):
        return self._def["description"]

    def _check_invalid_type(self, input):
        parsed_type = self._get_type(input)

        if parsed_type is not self._type:
            ctx = self._get_or_return_ctx(input)
            add_issue_to_context(
                ctx,
                code=ZodIssueCode.invalid_type,
                expected=self._type,
                received=ctx.parsed_type,
            )

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
            common=Common(issues=[], context_error_map=params.get("error_map")),
            path=params.get("path", []),
            schema_error_map=self._def.get("error_map"),
            parent=None,
            data=data,
            parsed_type=get_parsed_type(data),
        )
        input = ParseInput(data, path=ctx.path, parent=ctx)
        result = self._parse(input)
        return handle_result(ctx, result)

    def optional(self):
        # TODO
        pass
        # return ZodOptional._create()


class ZodString(ZodType):
    _type = ZodParsedType.string

    def _parse(self, input: ParseInput):
        if self._check_invalid_type(input):
            return INVALID

        status = ParseStatus()
        ctx = None
        for check in self._def["checks"]:
            kind = check["kind"]

            if kind == "min":
                if len(input.data) < check["value"]:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_small,
                        minimum=check["value"],
                        type="string",
                        inclusive=True,
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "max":
                if len(input.data) > check["value"]:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_big,
                        maximum=check["value"],
                        type="string",
                        inclusive=True,
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "email":
                if not regex.EMAIL.match(input.data):
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation="email",
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "uuid":
                if not regex.UUID.match(input.data):
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation="uuid",
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "url":
                url_valid = True
                if not is_server_side():
                    from anvil.js.window import URL

                    try:
                        URL(input.data)
                    except Exception:
                        url_valid = False
                else:
                    url_valid = regex.URL.match(input.data)
                if not url_valid:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation="url",
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "regex":
                match = check["regex"].match(input.data)
                if match is None:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation="regex",
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "strip":
                input.data = input.data.strip()

            elif kind == "startswith":
                if not input.data.startswith(check["value"]):
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation={"startswith": check["value"]},
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "endswith":
                if not input.data.endswith(check["value"]):
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation={"endswith": check["value"]},
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "datetime" or kind == "date":
                format = check["format"]
                try:
                    if format is not None:
                        datetime.strptime(input.data, format)
                    elif kind == "datetime":
                        datetime.fromisoformat(input.data)
                    else:
                        date.fromisoformat(input.data)
                except Exception:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.invalid_string,
                        validation=kind,
                        msg=check["msg"],
                    )
                    status.dirty()

            else:
                assert False

        return ParseReturn(status=status.value, value=input.data)

    def _add_check(self, **check):
        return ZodString({**self._def, "checks": [*self._def["checks"], check]})

    def email(self, msg=""):
        return self._add_check(kind="email", msg=msg)

    def url(self, msg=""):
        return self._add_check(kind="url", msg=msg)

    def uuid(self, msg=""):
        return self._add_check(kind="uuid", msg=msg)

    def datetime(self, format=None, msg=""):
        return self._add_check(kind="datetime", format=format, msg=msg)

    def date(self, format=None, msg=""):
        return self._add_check(kind="date", format=format, msg=msg)

    def regex(self, regex, msg=""):
        return self._add_check(kind="uuid", regex=regex, msg=msg)

    def startswith(self, value, msg=""):
        return self._add_check(kind="startswith", value=value, msg=msg)

    def endswith(self, value, msg=""):
        return self._add_check(kind="endswith", value=value, msg=msg)

    def min(self, min_length: int, msg=""):
        return self._add_check(kind="min", value=min_length, msg=msg)

    def max(self, min_length: int, msg=""):
        return self._add_check(kind="max", value=min_length, msg=msg)

    def len(self, len: int, msg=""):
        return self.min(len, msg).max(len, msg)

    def nonempty(self, msg=""):
        return self.min(1, msg)

    def strip(self):
        return self._add_check(kind="strip")

    @classmethod
    def _create(cls, **params):
        _def = {
            "checks": [],
            **process_params(**params),
        }
        return cls(_def)


class ZodNumber(ZodType):
    _type = ZodParsedType.number
    pass


class ZodBoolean(ZodType):
    _type = ZodParsedType.boolean

    def _parse(self, input: ParseInput):
        if self._check_invalid_type(input):
            return INVALID
        return OK(input.data)


class ZodNone(ZodType):
    _type = ZodParsedType.none

    def _parse(self, input: ParseInput):
        if self._check_invalid_type(input):
            return INVALID
        return OK(input.data)


class ZodAny(ZodType):
    def _parse(self, input):
        return OK(input.data)


class ZodUnknown(ZodType):
    _type = ZodParsedType.unknown
    _unknown = True

    def _parse(self, input):
        return OK(input.data)


class ZodNever(ZodType):
    _type = ZodParsedType.never

    def _parse(self, input):
        ctx = self._get_or_return_ctx(input)
        add_issue_to_context(
            ctx,
            code=ZodIssueCode.invalid_type,
            expected=self._type,
            received=ctx.parsed_type,
        )
        return INVALID


class ZodLiteral(ZodType):
    def _parse(self, input):
        value = self._def["value"]
        data = input.data
        if value is data or (type(value) is type(data) and value == data):
            return ParseReturn(status=VALID, value=data)
        else:
            ctx = self._get_or_return_ctx(input)
            add_issue_to_context(ctx, code=ZodIssueCode.invalid_literal, expected=value)
            return INVALID

    @property
    def value(self):
        return self._def["value"]

    @classmethod
    def create(cls, value, **params):
        return cls(
            {
                "value": value,
                **process_params(**params),
            }
        )


string = ZodString._create
boolean = ZodBoolean._create
none = ZodNone._create
any_ = ZodAny._create
unknown = ZodUnknown._create
never = ZodNever._create
literal = ZodLiteral._create
