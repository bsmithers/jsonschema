import numbers

from jsonschema.compat import str_types, int_types


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