# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import date, datetime
from typing import Optional

from anvil import is_server_side

from client_code.zod.helpers.error_util import error_to_obj

from ._errors import ZodError, ZodIssueCode
from .helpers import ZodParsedType, get_parsed_type, regex
from .helpers.parse_util import (
    DIRTY,
    INVALID,
    MISSING,
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


class ParseInputLazyPath:
    def __init__(self, parent, value, path, key):
        self.parent = parent
        self.data = value
        self._path = path
        self._key = key

    @property
    def path(self):
        return self._path + [self._key]


def handle_result(ctx, result):
    if is_valid(result):
        return ParseResult(success=True, data=result.value, error=None)
    else:
        if not ctx.common.issues:
            raise Exception("Validation failed but no issues detected")
        error = ZodError(ctx.common.issues)
        return ParseResult(success=False, data=None, error=error)


def process_params(
    error_map=None, invalid_type_error=False, required_error=False, **extra
):
    if not any([error_map, invalid_type_error, required_error]):
        return extra
    if error_map and (invalid_type_error or required_error):
        raise Exception(
            'Can\'t use "invalid_type_error" or "required_error" in conjunction with custom error'
        )

    if error_map:
        return {"error_map": error_map, **extra}

    def custom_map(iss, ctx):
        if iss["code"] != "invalid_type":
            return {"msg": ctx.default_error}
        # TODO

    return {"error_map": custom_map, **extra}


class ZodType:
    _type = None

    @classmethod
    def _create(cls, **params):
        return cls(process_params(**params))

    def __init__(self, _def):
        self._def = _def

    @property
    def description(self):
        return self._def["description"]

    def _check_invalid_type(self, input):
        parsed_type = self._get_type(input)

        types = self._type if type(self._type) is list else [self._type]

        if parsed_type not in types:
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

    def _add_check(self, **check):
        return type(self)({**self._def, "checks": [*self._def["checks"], check]})

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
        return ZodOptional._create(self)

    def nullable(self):
        return ZodNullable._create(self)

    def default(self, value):
        default = value
        if not callable(value):
            default = lambda: value  # noqa E731
        return ZodDefault({"inner_type": self, "default": default})

    def or_(self, other):
        return ZodUnion._create([self, other])

    def and_(self, other):
        pass


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
        return super()._create(checks=[], **params)


class ZodAbstractNumber(ZodType):
    _type = ZodParsedType.number

    def _parse(self, input):
        if self._check_invalid_type(input):
            return INVALID

        status = ParseStatus()
        ctx = None

        for check in self._def["checks"]:
            kind = check["kind"]

            if kind == "min":
                value = check["value"]
                inclusive = check["inclusive"]
                too_small = input.data < value if inclusive else input.data <= value
                if too_small:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_small,
                        minimum=value,
                        type=self._type,
                        inclusive=inclusive,
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "max":
                value = check["value"]
                inclusive = check["inclusive"]
                too_big = input.data > value if inclusive else input.data >= value
                if too_big:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_big,
                        minimum=value,
                        type=self._type,
                        inclusive=inclusive,
                        msg=check["msg"],
                    )
                    status.dirty()

            else:
                assert False

        return ParseReturn(statu=status.value, value=input.data)

    def _add_check(self, **check):
        return type(self)({**self._def, "checks": [*self._def["checks"], check]})

    def set_limit(self, kind, value, inclusive, msg=""):
        return self._add_check(kind=kind, value=value, inclusive=inclusive, msg=msg)

    def ge(self, value, msg=""):
        return self.set_limit("min", value, True, msg)

    min = ge

    def gt(self, value, msg=""):
        return self.set_limit("min", value, False, msg)

    def le(self, value, msg=""):
        return self.set_limit("max", value, True, msg)

    max = le

    def lt(self, value, msg=""):
        return self.set_limit("max", value, False, msg)

    def positive(self, msg=""):
        return self.set_limit("min", 0, False, msg)

    def negative(self, msg=""):
        return self.set_limit("max", 0, False, msg)

    def nonpositive(self, msg=""):
        return self.set_limit("max", 0, True, msg)

    def nonnegative(self, msg=""):
        return self.set_limit("min", 0, True, msg)

    @classmethod
    def _create(cls, **params):
        return super()._create(checks=[], **params)


class ZodInteger(ZodAbstractNumber):
    _type = ZodParsedType.integer


class ZodFloat(ZodAbstractNumber):
    _type = ZodParsedType.float


class ZodNumber(ZodAbstractNumber):
    _type = [ZodParsedType.integer, ZodParsedType.float]


class ZodDateTime(ZodType):
    _type = ZodParsedType.datetime

    def _parse(self, input):
        if self._check_invalid_type(input):
            return INVALID

        status = ParseStatus()
        ctx = None
        for check in self._def["checks"]:
            kind = check["kind"]

            if kind == "min":
                if input.data < check["value"]:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_small,
                        minimum=check["value"],
                        type=self._type,
                        inclusive=True,
                        msg=check["msg"],
                    )
                    status.dirty()

            elif kind == "max":
                if input.data > check["value"]:
                    ctx = self._get_or_return_ctx(input, ctx)
                    add_issue_to_context(
                        ctx,
                        code=ZodIssueCode.too_big,
                        maximum=check["value"],
                        type=self._type,
                        inclusive=True,
                        msg=check["msg"],
                    )
                    status.dirty()

            else:
                assert False

        return ParseReturn(status=status.value, value=input.data)

    def min(self, min_date: int, msg=""):
        return self._add_check(kind="min", value=min_date, msg=msg)

    def max(self, max_date: int, msg=""):
        return self._add_check(kind="max", value=max_date, msg=msg)

    @classmethod
    def _create(cls, **params):
        return super()._create(checks=[], **params)


class ZodDate(ZodDateTime):
    _type = ZodParsedType.date


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


class ZodObject(ZodType):
    _type = ZodParsedType.mapping

    def __init__(self, _def):
        super().__init__(_def)
        self._cached = None

    def _get_cached(self):
        if self._cached is not None:
            return self._cached

        shape = self._def["shape"]()
        keys = shape.keys()

        self._cached = (shape, keys)

        return self._cached

    def _parse(self, input):
        if self._check_invalid_type(input):
            return INVALID

        status, ctx = self._process_input_params(input)
        shape, shape_keys = self._get_cached()
        extra_keys = set()

        if not (
            type(self._def["catchall"]) is ZodNever
            and self._def["unknown_keys"] == "strip"
        ):
            for key in ctx.data:
                if key not in shape_keys:
                    extra_keys.add(key)

        pairs = []

        for key in shape_keys:
            key_validator = shape[key]
            value = ctx.data.get(key, MISSING)
            pairs.append(
                (
                    ParseReturn(VALID, key),
                    key_validator._parse(ParseInputLazyPath(ctx, value, ctx.path, key)),
                    key in ctx.data,
                )
            )

        if type(self._def["catchall"]) is ZodNever:
            unknown_keys = self._def["unknown_keys"]
            if unknown_keys == "passthrough":
                for key in extra_keys:
                    pairs.append(
                        ParseReturn(VALID, key),
                        ParseReturn(VALID, ctx.data[key], False),
                    )
            elif unknown_keys == "strict":
                if extra_keys:
                    add_issue_to_context(
                        ctx, code=ZodIssueCode.unrecognized_keys, keys=extra_keys
                    )
                    status.dirty()
            elif unknown_keys == "strip":
                pass
            else:
                assert False, "invalid unknown_keys value"
        else:
            # run cachall validation
            catchall = self._def["catchall"]

            for key in extra_keys:
                value = ctx.data[key]
                pairs.append(
                    ParseReturn(VALID, key),
                    catchall._parse(
                        ParseInputLazyPath(ctx, value, ctx.path, key), key in ctx.data
                    ),
                )

        return ParseStatus.merge_dict(status, pairs)

    @property
    def shape(self):
        return self._def["shape"]

    def strict(self, msg=""):
        _def = {**self._def, "unknown_keys": "strict"}
        if msg:

            def error_map(issue, ctx):
                try:
                    default_error = self._def["error_map"](issue, ctx)["msg"]
                except TypeError:
                    default_error = ctx.default_error
                if issue.code == "unrecognized_keys":
                    return {"msg": error_to_obj(msg)["msg"] or default_error}
                return {"msg": default_error}

            _def["error_map"] = error_map
        return ZodObject(_def)

    def strip(self):
        return ZodObject({**self._def, "unknown_keys": "strip"})

    def passthrough(self):
        return ZodObject({**self._def, "unknown_keys": "passthrough"})

    def catchall(self, index):
        return ZodObject({**self._def, "catchall": index})

    @classmethod
    def _create(cls, shape, **params):
        return super()._create(
            shape=lambda: shape, unknown_keys="strip", catchall=never(), **params
        )


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
    def _create(cls, value, **params):
        return super()._create(value=value, **params)


class ZodWraps(ZodType):
    _wraps = None
    _type = None

    def _parse(self, input):
        parse_type = self._get_type(input)
        if parse_type is self._type:
            return OK(self._wraps)
        return self._def["inner_type"]._parse(input)

    def unwrap(self):
        return self._def["inner_type"]

    @classmethod
    def _create(cls, type, **params):
        return super()._create(inner_type=type, **params)


class ZodOptional(ZodWraps):
    _wraps = MISSING
    _type = ZodParsedType.missing


class ZodNullable(ZodWraps):
    _wraps = None
    _type = ZodParsedType.none


class ZodDefault(ZodType):
    def _parse(self, input):
        ctx = self._get_or_return_ctx(input)
        data = ctx.data
        if ctx.parsed_type is not ZodParsedType.missing:
            data = self._def["default"]()
        return self._def["inner_type"]._parse(data, path=ctx.path, parent=ctx)

    @classmethod
    def _create(cls, type, default, **params):
        default_ = default
        if not callable(default):
            default_ = lambda: default  # noqa E731
        return super()._create(inner_type=type, default=default_, **params)


class ZodUnion(ZodType):
    def _parse(self, input):
        ctx = self._get_or_return_ctx(input)
        options = self._def["options"]
        dirty = None
        all_issues = []

        for option in options:
            # child_ctx = ...
            child_ctx = ParseContext(
                **{**ctx, "common": Common(**{**ctx.common, "parent": None})}
            )

            result = option._parse(
                ParseInput(data=ctx.data, path=ctx.path, parent=child_ctx)
            )

            if result.status is VALID:
                return result
            elif result.status is DIRTY and not dirty:
                dirty = {"result": result, "ctx": child_ctx}

            if child_ctx.common.issues:
                all_issues.append(child_ctx.common.issues)  # should this be extend?

        if dirty:
            ctx.common.issues.extend(dirty["ctx"].common.issues)
            return dirty["result"]

        union_errors = [ZodError(issues) for issues in all_issues]
        add_issue_to_context(
            ctx, code=ZodIssueCode.invalid_union, union_erros=union_errors
        )
        return INVALID

    @property
    def options(self):
        return self._def["options"]

    @classmethod
    def _create(cls, types, **params):
        return super()._create(options=types, **params)


string = ZodString._create
boolean = ZodBoolean._create
none = ZodNone._create
any_ = ZodAny._create
unknown = ZodUnknown._create
never = ZodNever._create
literal = ZodLiteral._create
optional = ZodOptional._create
nullable = ZodNullable._create
date_ = ZodDate._create
datetime_ = ZodDateTime._create
integer = ZodInteger._create
float = ZodFloat._create
number = ZodNumber._create
union = ZodUnion._create
