import numbers

import attr
import pyrsistent

from jsonschema import _utils
from jsonschema.compat import str_types, int_types, iteritems
from jsonschema.exceptions import UnknownTypeName


def is_array(instance):
    return isinstance(instance, list)


def is_bool(instance):
    return isinstance(instance, bool)


def is_integer(instance):
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, int_types)


def is_null(instance):
    return instance is None


def is_number(instance):
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, numbers.Number)


def is_object(instance):
    return isinstance(instance, dict)


def is_string(instance):
    return isinstance(instance, str_types)


def is_any(instance):
    return True


def is_integer_draft6(instance):
    if isinstance(instance, float) and instance.is_integer():
        return True
    return is_integer(instance)


@attr.s(frozen=True)
class TypeChecker(object):
    type_checkers = attr.ib(default=pyrsistent.pmap({}))

    def is_type(self, instance, type_):
        if type_ not in self.type_checkers:
            raise UnknownTypeName

        function_or_type = self.type_checkers[type_]
        if isinstance(function_or_type, (type, tuple)):
            return self._deprecated_type_check(instance, function_or_type)

        return function_or_type(instance)

    def update(self, redefine=(), remove=()):
        redefine = dict(redefine)
        evolver = self.type_checkers.evolver()

        for type_, checker in iteritems(redefine):
            evolver[type_] = checker

        for type_ in remove:
            try:
                del evolver[type_]
            except KeyError:
                raise UnknownTypeName

        return attr.evolve(self, type_checkers=evolver.persistent())

    def _deprecated_type_check(self, instance, pytypes):

        # bool inherits from int, so ensure bools aren't reported as ints
        if isinstance(instance, bool):
            pytypes = _utils.flatten(pytypes)
            is_number = any(
                issubclass(pytype, numbers.Number) for pytype in pytypes
            )
            if is_number and bool not in pytypes:
                return False
        return isinstance(instance, pytypes)


draft3_type_checker = TypeChecker().update(redefine={
    u"any": is_any,
    u"array": is_array,
    u"boolean": is_bool,
    u"integer": is_integer,
    u"object": is_object,
    u"null": is_null,
    u"number": is_number,
    u"string": is_string
})

draft4_type_checker = draft3_type_checker.update(remove={u"any"})

draft6_type_checker = draft4_type_checker.update(redefine={
    u"integer": is_integer_draft6
})