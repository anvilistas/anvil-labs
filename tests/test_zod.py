# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas
import operator as op
from datetime import date, datetime
from functools import partial

import pytest

import client_code.zod as z

__version__ = "0.0.1"

MISSING = z._types.MISSING


def check_error_message(schema, val, message):
    try:
        schema.parse(val)
    except z.ParseError as e:
        assert e.message == message
    else:
        pytest.fail()


def check_throws(schema, val):
    with pytest.raises(z.ParseError):
        schema.parse(val)


def test_validation():
    for schema, val, message in [
        (z.array(z.string()).min(4), [], "Array must contain at least 4 element(s)"),
        (
            z.array(z.string()).max(2),
            ["asdf", "asdf", "asdf"],
            "Array must contain at most 2 element(s)",
        ),
        (z.string().min(4), "asd", "String must contain at least 4 character(s)"),
        (z.string().max(4), "aasdfsdfsd", "String must contain at most 4 character(s)"),
        (z.number().ge(3), 2, "Number must be greater than or equal to 3"),
        (z.number().le(3), 4, "Number must be less than or equal to 3"),
        (z.number().nonnegative(), -1, "Number must be greater than or equal to 0"),
        (z.number().nonpositive(), 1, "Number must be less than or equal to 0"),
        (z.number().negative(), 1, "Number must be less than 0"),
        (z.number().positive(), -1, "Number must be greater than 0"),
    ]:
        check_error_message(schema, val, message)


def test_str_instantiation():
    for schema in (
        z.string().min(5),
        z.string().max(5),
        z.string().len(5),
        z.string().email(),
        z.string().url(),
        z.string().uuid(),
        z.string().min(5, message="Must be 5 or more characters long"),
        z.string().max(5, message="Must be 5 or fewer characters long"),
        z.string().len(5, message="Must be exactly 5 characters long"),
        z.string().email(message="Invalid email address."),
        z.string().url(message="Invalid url"),
        z.string().uuid(message="Invalid UUID"),
    ):
        assert isinstance(schema, z._types.ZodString)


def test_array():
    minTwo = z.string().array().min(2)
    maxTwo = z.string().array().max(2)
    justTwo = z.string().array().len(2)
    intNum = z.string().array().nonempty()
    nonEmptyMax = z.string().array().nonempty().max(2)

    # successful
    minTwo.parse(["a", "a"])
    minTwo.parse(["a", "a", "a"])
    maxTwo.parse(["a", "a"])
    maxTwo.parse(["a"])
    justTwo.parse(["a", "a"])
    intNum.parse(["a"])
    nonEmptyMax.parse(["a"])

    a = ["a"]

    for schema, val in [
        (minTwo, a),
        (maxTwo, a * 3),
        (justTwo, a),
        (justTwo, a * 3),
        (intNum, []),
        (nonEmptyMax, []),
        (nonEmptyMax, a * 3),
    ]:
        check_throws(schema, val)

    check_throws(z.array(z.string()).nonempty(), [])

    assert justTwo.element.parse("asdf")
    check_throws(justTwo.element, 42)

    schema = z.object({"people": z.string().array().min(2)})
    result = schema.safe_parse({"people": [123]})
    assert not result.success
    assert len(result.error.issues) == 2


def test_catch():

    string_with_default = z.string().catch("default")
    for x in (None, True, 42, [], {}, object()):
        assert string_with_default.parse(x) == "default"

    string_with_default = z.string().transform(str.upper).catch("default")
    assert string_with_default.parse(None) == "default"
    assert string_with_default.parse(42) == "default"
    assert isinstance(string_with_default._def["inner_type"], z._types.ZodEffects)

    string_with_default = z.string().optional().catch("asdf")
    assert string_with_default.parse(None) == "asdf"
    assert string_with_default.parse(42) == "asdf"
    assert isinstance(string_with_default._def["inner_type"], z._types.ZodOptional)

    complex = (
        z.string()
        .catch("asdf")
        .transform(lambda s, _: s + "!")
        .transform(str.upper)
        .catch("qwer")
        .remove_default()
        .optional()
        .catch("asdfasdf")
    )

    assert complex.parse("qwer") == "QWER!"
    assert complex.parse(42) == "ASDF!"
    assert complex.parse(True) == "ASDF!"

    inner = z.string().catch("asdf")
    outer = z.object({"inner": inner}).catch({"inner": "asdf"})

    assert outer.parse(None) == {"inner": "asdf"}
    assert outer.parse({}) == {"inner": "asdf"}
    assert outer.parse({"inner": None}) == {"inner": "asdf"}

    assert z.string().catch("inner").catch("outer").parse(3) == "inner"

    schema = z.object(
        {
            "fruit": z.enum(["apple", "orange"]).catch("apple"),
        }
    )
    assert schema.parse({}) == {"fruit": "apple"}
    assert schema.parse({"fruit": True}) == {"fruit": "apple"}
    assert schema.parse({"fruit": 42}) == {"fruit": "apple"}


def test_crazy_schema():
    crazySchema = z.object(
        {
            "tuple": z.tuple(
                [
                    z.string().nullable().optional(),
                    z.number().nullable().optional(),
                    z.boolean().nullable().optional(),
                    z.none().nullable().optional(),
                    z.literal("1234").nullable().optional(),
                ]
            ),
            "merged": z.object(
                {
                    "k1": z.string().optional(),
                }
            ).merge(z.object({"k1": z.string().nullable(), "k2": z.number()})),
            "union": z.array(z.union([z.literal("asdf"), z.literal(12)])).nonempty(),
            "array": z.array(z.number()),
            "sumMinLength": z.array(z.number()).refine(lambda arg: len(arg) > 5),
            "enum": z.enum(["zero", "one"]),
            "nonstrict": z.object({"points": z.number()}).passthrough(),
        }
    )

    crazySchema.parse(
        {
            "tuple": ["asdf", 1234, True, None, "1234"],
            "merged": {"k1": "asdf", "k2": 12},
            "union": ["asdf", 12, "asdf", 12, "asdf", 12],
            "array": [12, 15, 16],
            "sumMinLength": [12, 15, 16, 98, 24, 63],
            "enum": "one",
            "nonstrict": {"points": 1234},
        }
    )


def date_test():

    before = date(2022, 10, 4)
    dt = date(2022, 10, 5)
    after = date(2022, 10, 6)

    min_check = z.date().min(dt)
    max_check = z.date().max(dt)

    min_check.parse(dt)
    min_check.parse(after)
    max_check.parse(dt)
    max_check.parse(before)

    check_throws(min_check, before)
    check_throws(max_check, after)


def test_default():

    string_with_default = z.string().default("default")
    assert string_with_default.parse(MISSING) == "default"

    string_with_default = z.string().transform(str.upper).default("default")
    assert string_with_default.parse(MISSING) == "DEFAULT"
    assert isinstance(string_with_default._def["inner_type"], z._types.ZodEffects)

    string_with_default = z.string().optional().default("asdf")
    assert string_with_default.parse(MISSING) == "asdf"
    assert isinstance(string_with_default._def["inner_type"], z._types.ZodOptional)

    complex = (
        z.string()
        .default("asdf")
        .transform(str.upper)
        .default("qwer")
        .remove_default()
        .optional()
        .default("asdfasdf")
    )

    assert complex.parse(MISSING) == "ASDFASDF"

    inner = z.string().default("asdf")
    outer = z.object({"inner": inner}).default({"inner": "asdf"})

    assert outer.parse(MISSING) == {"inner": "asdf"}
    assert outer.parse({}) == {"inner": "asdf"}

    assert z.string().default("inner").default("outer").parse(MISSING) == "outer"

    schema = z.object(
        {
            "fruit": z.enum(["apple", "orange"]).default("apple"),
        }
    )
    assert schema.parse({}) == {"fruit": "apple"}


def test_enum():
    myenum = z.enum(["Red", "Green", "Blue"])
    assert myenum.enum.Red == "Red"
    assert myenum.options == ["Red", "Green", "Blue"]

    check_throws(myenum, "Yellow")

    result = z.enum(["test"], required_error="REQUIRED").safe_parse(MISSING)

    assert not result.success
    assert result.error.message == "REQUIRED"


def test_isinstance():
    class Test:
        pass

    class SubTest(Test):
        pass

    test_schema = z.isinstance(Test)
    sub_test_schema = z.isinstance(SubTest)

    test_schema.parse(Test())
    test_schema.parse(SubTest())
    sub_test_schema.parse(SubTest())

    check_throws(sub_test_schema, Test())
    check_throws(test_schema, 42)

    schema = z.isinstance(date).refine(str)
    res = schema.safe_parse(None)
    assert not res.success


def test_nullable():
    def check_errors(a, bad):
        expected = None
        try:
            a.parse(bad)
        except z.ParseError as e:
            expected = e.message
        else:
            pytest.fail()

        try:
            a.nullable().parse(bad)
        except z.ParseError as e:
            assert e.message == expected
        else:
            pytest.fail()

    check_errors(z.string().min(2), 1)
    z.string().min(2).nullable().parse(None)
    check_errors(z.number().ge(2), 1)
    z.number().ge(2).nullable().parse(None)
    check_errors(z.boolean(), "")
    z.boolean().nullable().parse(None)
    check_errors(z.none(), {})
    z.none().nullable().parse(None)
    check_errors(z.none(), {})
    z.none().nullable().parse(None)
    check_errors(z.object({}), 1)
    z.object({}).nullable().parse(None)
    check_errors(z.tuple([]), 1)
    z.tuple([]).nullable().parse(None)
    # check_errors(z.unknown(), 1)
    z.unknown().nullable().parse(None)


def test_number():
    gtFive = z.number().gt(5)
    gteFive = z.number().ge(5)
    ltFive = z.number().lt(5)
    lteFive = z.number().le(5)
    # intNum = z.number().int()
    # multipleOfFive = z.number().multipleOf(5)
    # finite = z.number().finite()
    # stepPointOne = z.number().step(0.1)
    # stepPointZeroZeroZeroOne = z.number().step(0.0001)
    # stepSixPointFour = z.number().step(6.4)
    z.number().parse(1)
    z.number().parse(1.5)
    z.number().parse(0)
    z.number().parse(-1.5)
    z.number().parse(-1)
    z.number().parse(float("inf"))
    z.number().parse(float("-inf"))
    gtFive.parse(6)
    gteFive.parse(5)
    ltFive.parse(4)
    lteFive.parse(5)
    # intNum.parse(4)
    # multipleOfFive.parse(15)
    # finite.parse(123)
    # stepPointOne.parse(6)
    # stepPointOne.parse(6.1)
    # stepPointOne.parse(6.1)
    # stepSixPointFour.parse(12.8)
    # stepPointZeroZeroZeroOne.parse(3.01)

    check_throws(ltFive, 5)
    check_throws(lteFive, 6)
    check_throws(gtFive, 5)
    check_throws(gteFive, 4)


def test_object_extend():
    Animal = z.object({"species": z.string()}).extend({"population": z.integer()})

    ModifiedAnimal = Animal.extend({"species": z.array(z.string())})

    ModifiedAnimal.parse({"species": ["asd"], "population": 42})

    check_throws(ModifiedAnimal, {"species": "asd", "population": 42})


def test_object():
    # TODO
    pass


def test_optional():
    def check_errors(a, bad):
        expected = None
        try:
            a.parse(bad)
        except z.ParseError as e:
            expected = e.message
        else:
            pytest.fail()

        try:
            a.optional().parse(bad)
        except z.ParseError as e:
            assert e.message == expected
        else:
            pytest.fail()

    check_errors(z.string().min(2), 1)
    z.string().min(2).optional().parse(MISSING)
    check_errors(z.number().ge(2), 1)
    z.number().ge(2).optional().parse(MISSING)
    check_errors(z.boolean(), "")
    z.boolean().optional().parse(MISSING)
    check_errors(z.none(), {})
    z.none().optional().parse(MISSING)
    check_errors(z.none(), {})
    z.none().optional().parse(MISSING)
    check_errors(z.object({}), 1)
    z.object({}).optional().parse(MISSING)
    check_errors(z.tuple([]), 1)
    z.tuple([]).optional().parse(MISSING)
    # check_errors(z.unknown(), 1)
    z.unknown().optional().parse(MISSING)


def test_parser():
    check_throws(
        z.object({"name": z.string()}).strict(), {"name": "bill", "unknownKey": 12}
    )

    check_throws(z.tuple([]), "12")
    check_throws(z.tuple([]), ["12"])
    check_throws(z.enum(["blue"]), "Red")


def test_partials():
    # TODO
    pass


def test_pick_omit():
    # TODO
    pass


def test_primitive():
    pass


def test_record():
    pass


def test_recursive():
    pass


def test_refine():
    pass


def test_safe_parse():
    pass


def test_string():
    pass


def test_transformer():
    pass


def test_tuple():
    testTuple = z.tuple(
        [
            z.string(),
            z.object({"name": z.literal("Rudy")}),
            z.array(z.literal("blue")),
        ]
    )
    testData = ["asdf", {"name": "Rudy"}, ["blue"]]
    badData = [123, {"name": "Rudy2"}, ["blue", "red"]]

    assert testTuple.parse(testData) == testData
    assert testTuple.parse(testData) is not testData

    with pytest.raises(z.ParseError) as e:
        testTuple.parse(badData)

    assert len(e.value.issues) == 3
    result = testTuple.safe_parse(badData)
    assert not result.success
    assert len(result.error.issues) == 3

    stringToNumber = z.string().transform(len)
    val = z.tuple([stringToNumber])
    assert val.parse(["1234"]) == [4]

    myTuple = z.tuple([z.string(), z.number()]).rest(z.boolean())
    x = ("asdf", 1234, True, False, True)
    assert myTuple.parse(x) == list(x)
    assert myTuple.parse(["a", 42]) == ["a", 42]

    check_throws(myTuple, ["asdf", 1234, "asdf"])


def test_unions():
    schema = z.union(
        [
            z.string().refine(lambda x: False),
            z.number().refine(lambda x: False),
        ]
    )
    assert not schema.safe_parse("asdf").success

    assert (
        not z.union([z.number(), z.string().refine(lambda x: False)])
        .safe_parse("a")
        .success
    )

    schema = z.union(
        [
            z.object(
                {
                    "email": z.string().email(),
                }
            ),
            z.string(),
        ]
    )

    assert schema.parse("asdf") == "asdf"
    assert schema.parse({"email": "asd@asd.com"}) == {"email": "asd@asd.com"}

    result = z.union([z.number(), z.string().refine(lambda x: False)]).safe_parse("a")
    assert not result.success
    assert result.error.message == "Invalid input"
    assert result.error.issues[0].code == "custom"

    union = z.union([z.string(), z.number()])
    union.options[0].parse("asdf")
    union.options[1].parse(1234)
