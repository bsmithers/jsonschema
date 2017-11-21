import numbers

import attr
import pyrsistent

from jsonschema.compat import str_types, int_types, iteritems
from jsonschema.exceptions import UndefinedTypeCheck


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
    """
    A ``type`` property checker.

    A :class:`TypeChecker` performs type checking for an instance of
    :class:`Validator`. Type checks to perform are set using
    :meth:`TypeChecker.redefine or :meth:`TypeChecker.redefine_many` and
    removed via :meth:`TypeChecker.remove` or
    :meth:`TypeChecker.remove_many`. Each of these return a new
    :class:`TypeChecker` object.

    Arguments:

        None
    """
    type_checkers = attr.ib(default=pyrsistent.pmap({}))

    def is_type(self, instance, type_):
        """
        Check if the instance is of the appropriate type.

        Arguments:

            instance (any primitive type, i.e. str, number, bool):

                The instance to check

            type_ (str):

                The name of the type that is expected.

        Returns:

            bool: Whether it conformed.


        Raises:

            :exc:`UndefinedTypeCheck` if type_ is unknown to this object.

        """
        try:
            return self.type_checkers[type_](instance)
        except KeyError:
            raise UndefinedTypeCheck

    def redefine(self, type_, fn):
        """
        Redefine the checker for type_ to the function fn.

        Arguments:

            type_ (str):

                The name of the type to check.

            fn (callable):

                A function taking exactly one parameter, instance,
                that checks if instance is of this type.

        Returns:

            A new :class:`TypeChecker` instance.

        """
        return self.redefine_many({type_:fn})

    def redefine_many(self, definitions=()):
        """
        Redefine multiple type checkers.

        Arguments:

            definitions (dict):

                A dictionary mapping types to their checking functions.

        Returns:

            A new :class:`TypeChecker` instance.

        """
        definitions = dict(definitions)
        evolver = self.type_checkers.evolver()

        for type_, checker in iteritems(definitions):
            evolver[type_] = checker

        return attr.evolve(self, type_checkers=evolver.persistent())

    def remove(self, type_):
        """
        Remove the type from the checkers that this object understands.

        Arguments:

            type_ (str):

                The name of the type to remove.

        Returns:

            A new :class:`TypeChecker` instance

        Raises:

            :exc:`UndefinedTypeCheck` if type_ is unknown to this object

        """
        return self.remove_many((type_,))

    def remove_many(self, types):
        """
        Remove multiple types from the checkers that this object understands.

        Arguments:

            types (iterable):

                An iterable of types to remove.

        Returns:

            A new :class:`TypeChecker` instance

        Raises:

            :exc:`UndefinedTypeCheck` if any of the types are unknown to
            this object

        """
        evolver = self.type_checkers.evolver()

        for type_ in types:
            try:
                del evolver[type_]
            except KeyError:
                raise UndefinedTypeCheck

        return attr.evolve(self, type_checkers=evolver.persistent())


draft3_type_checker = TypeChecker().redefine_many({
    u"any": is_any,
    u"array": is_array,
    u"boolean": is_bool,
    u"integer": is_integer,
    u"object": is_object,
    u"null": is_null,
    u"number": is_number,
    u"string": is_string
})

draft4_type_checker = draft3_type_checker.remove(u"any")

draft6_type_checker = draft4_type_checker.redefine(u"integer",
                                                   is_integer_draft6)