# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

from datetime import date, datetime

from .._zod_error import ZodIssueCode
from ..helpers import ZodParsedType
from ..helpers.parse_util import ErrorMapContext
from ..helpers.util import join

__version__ = "0.0.1"


def error_map(issue, _ctx: ErrorMapContext):
    msg = ""
    code = issue["code"]
    if code == ZodIssueCode.invalid_type:
        if issue["received"] == ZodParsedType.missing:
            msg = "Required"
        else:
            msg = f"Expected {issue['expected']}, received {issue['received']}"

    elif code == ZodIssueCode.invalid_literal:
        msg = f"Invalid literal value, expected {issue['expected']!r}"

    elif code == ZodIssueCode.unrecognized_keys:
        msg = f"Unrecognized key(s) in object: {join(issue['keys'], ', ')}"

    elif code == ZodIssueCode.invalid_union:
        msg = "Invalid input"

    # elif code == ZodIssueCode.invalid_union_discriminator:
    #     msg = f"Invalid discriminator value. Expected {join(issue['options'])}"

    elif code == ZodIssueCode.invalid_enum_value:
        msg = f"Invalid enum value. Expected {join(issue['options'])}, received {issue['received']!r}"

    # elif code == ZodIssueCode.invalid_arguments:
    #     msg = "Invalid function arguments"

    # elif code == ZodIssueCode.invalid_return_type:
    #     msg = "Invalid function return type"

    elif code == ZodIssueCode.invalid_date:
        msg = "Invalid date"

    elif code == ZodIssueCode.invalid_string:
        if type(issue["validation"]) is dict:
            if "startswith" in issue["validation"]:
                msg = f"Invalid input: must start with {issue['validation']['startswith']!r}"
            elif "endswith" in issue["validation"]:
                msg = (
                    f"Invalid input: must end with {issue['validation']['endswith']!r}"
                )
            else:
                assert False, issue["validation"]

        elif issue["validation"] != "regex":
            msg = f"Invalid {issue['validation']}"
        else:
            msg = "Invalid"

    elif code == ZodIssueCode.too_small:
        if issue["type"] == "array":
            msg = f"Array must contain {'at least' if issue['inclusive'] else 'more than'} {issue['minimum']} element(s)"
        elif issue["type"] == "string":
            msg = f"String must contain {'at least' if issue['inclusive'] else 'over'} {issue['minimum']} character(s)"
        elif issue["type"] in ("number", "date", "integer", "float", "datetime"):
            msg = f"{issue['type'].capitalize()} must be greater than {'or equal to ' if issue['inclusive'] else ''}{issue['minimum']}"
        else:
            msg = "Invalid input"

    elif code == ZodIssueCode.too_big:
        if issue["type"] == "array":
            msg = f"Array must contain {'at most' if issue['inclusive'] else 'less than'} {issue['maximum']} element(s)"
        elif issue["type"] == "string":
            msg = f"String must contain {'at most' if issue['inclusive'] else 'under'} {issue['maximum']} character(s)"
        elif issue["type"] in ("number", "date", "integer", "float", "datetime"):
            msg = f"{issue['type'].capitalize()} must must be less than {'or equal to ' if issue['inclusive'] else ''}{issue['maximum']}"
        else:
            msg = "Invalid input"

    elif code == ZodIssueCode.custom:
        msg = "Invalid input"

    # elif code == ZodIssueCode.invalid_intersection_types:
    #   msg = f"Intersection results could not be merged"

    # elif code == ZodIssueCode.not_multiple_of:
    #   msg = f"Number must be a multiple of {issue['multipleOf']}"

    # elif code == ZodIssueCode.not_finite:
    #   msg = "Number must be finite"

    else:
        assert False, "Unknown error code"

    return {"msg": msg}
