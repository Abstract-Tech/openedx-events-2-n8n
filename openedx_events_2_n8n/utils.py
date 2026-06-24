"""
Utilities used by Open edX Events handlers.
"""

import json
from collections.abc import MutableMapping

from django.core.serializers.json import DjangoJSONEncoder
from opaque_keys.edx.locator import CourseLocator


def flatten_dict(dictionary, parent_key="", sep="_"):
    """
    Generate a flatten dictionary-like object.

    Taken from:
    https://stackoverflow.com/a/6027615/16823624
    """
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def make_json_serializable(data):
    """
    Convert Django/Open edX event data into plain JSON-compatible values.
    """
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def serialize_course_key(inst, field, value):  # pylint: disable=unused-argument
    """
    Serialize instances of CourseLocator.

    When value is anything else returns it without modification.
    """
    if isinstance(value, CourseLocator):
        return str(value)
    return value
