"""
Tests on the new type interface. Reproducing the json-schema type tests on
the built-in functions seems of little value, so this focuses on extensions
"""
from collections import namedtuple
from unittest import TestCase

from jsonschema import _types, ValidationError, _validators
from jsonschema.validators import Draft6Validator, extend


def type_ints_or_string_ints(instance):
    if _types.is_integer(instance):
        return True

    if _types.is_string(instance):
        try:
            int(instance)
            return True
        except ValueError:
            pass
    return False


def is_namedtuple(instance):
    if isinstance(instance, tuple) and getattr(instance, '_fields',
                                               None):
        return True

    return False


def type_object_allow_namedtuples(instance):
    if _types.is_object(instance):
        return True

    if is_namedtuple(instance):
        return True

    return False


def coerce_named_tuple(fn):
    def coerced(validator, required, instance, schema):
        if is_namedtuple(instance):
            instance = instance._asdict()
        return fn(validator, required, instance, schema)
    return coerced

required = coerce_named_tuple(_validators.required)
properties = coerce_named_tuple(_validators.properties)


class TestCustomTypes(TestCase):

    def test_simple_type_can_be_extended(self):
        schema = {'type': 'integer'}

        CustomValidator = extend(Draft6Validator,
                   type_checks={"integer": type_ints_or_string_ints})

        v = CustomValidator(schema)
        v.validate(4)
        v.validate('4')

        with self.assertRaises(ValidationError):
            v.validate(4.4)

    def test_object_can_be_extended(self):
        schema = {'type': 'object'}

        Point = namedtuple('Point', ['x', 'y'])

        CustomValidator = extend(Draft6Validator,
                                 type_checks={
                                     "object": type_object_allow_namedtuples})

        v = CustomValidator(schema)
        v.validate(Point(x=4, y=5))

    def test_object_extensions_require_custom_validators(self):
        schema = {'type': 'object', 'required': ['x']}

        CustomValidator = extend(Draft6Validator,
                                 type_checks={
                                     "object":
                                         type_object_allow_namedtuples})

        v = CustomValidator(schema)
        Point = namedtuple('Point', ['x', 'y'])
        # Cannot handle required
        with self.assertRaises(ValidationError):
            v.validate(Point(x=4, y=5))

    def test_object_extensions_can_handle_custom_validators(self):
        schema = {'type': 'object',
                  'required': ['x'],
                  'properties': {'x':
                                     {'type': 'integer'}
                                 }
                  }

        CustomValidator = extend(Draft6Validator,
                                 type_checks={
                                     "object":
                                         type_object_allow_namedtuples},
                                 validators={"required": required,
                                             'properties': properties})

        v = CustomValidator(schema)

        Point = namedtuple('Point', ['x', 'y'])
        # Can now process required and properties
        v.validate(Point(x=4, y=5))

        with self.assertRaises(ValidationError):
            v.validate(Point(x="not an integer", y=5))


    def test_old_default_types_valid(self):
        # TODO Here or in TestCreateExtend
        pass

    def test_old_types_valid(self):
        # TODO Here or in TestCreateExtend
        pass
