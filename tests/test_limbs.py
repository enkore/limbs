import os
import io

import pytest
from limbs import load, dump, loads, dumps


def get_file_path(name):
    return os.path.join(os.path.dirname(__file__), name)


@pytest.fixture
def simple_object():
    class O:
        def __init__(self):
            self.field_one = "Has A Value"
            self.field_two = "is field two"
    return O()


def test_load_simple():
    with open(get_file_path("simple.limbs"), "rb") as fd:
        o = load(fd)

    assert o.field_one == "Has A Value"
    assert o.field_two == "is field two"
    assert o.superfluous == "surrounding space is trimmed"
    assert hasattr(o, "space_before")
    assert o.double == "overwritten"
    assert o.fields_can == """span multiple lines
by indenting them with one or more
spaces, however, all lines except the first
need to have the same number of spaces,
which are removed.
  Thus extra leading space is preserved."""
    assert o.utf_8 == "is the \u00e4nc\u00f6ding of choice."
    assert o.from_

    # note that it's a byte string
    assert o.body == b"""The body consists of arbitrary data and is separated with a single empty line
from the header. In contrast to the header neither the encoding nor the format
is specified - the body is simply a bytestring."""


def test_dump_simple(simple_object):
    ss = io.BytesIO()
    dump(simple_object, ss)

    assert ss.getvalue().decode("utf-8") == """Field-One: Has A Value
Field-Two: is field two
"""


def test_dump_load(simple_object):
    ss = io.BytesIO()
    dump(simple_object, ss)

    ss.seek(0, io.SEEK_SET)
    wrapped = io.BufferedReader(ss)
    recovered_object = load(wrapped)

    assert recovered_object.field_one == simple_object.field_one
    assert recovered_object.field_two == simple_object.field_two


def test_dump_loads(simple_object):
    ss = io.BytesIO()
    dump(simple_object, ss)

    recovered_object = loads(ss.getvalue())

    assert recovered_object.field_one == simple_object.field_one
    assert recovered_object.field_two == simple_object.field_two


def test_invalid_name():
    with pytest.raises(ValueError):
        loads(b"121-Invalid-Name: abdef")


def test_unicode_name():
    loads("Töhis-Is-Ä-Välid-Näim: abdef".encode("utf-8"))
    loads("Üi-can-start-With-Umlauts: abdef".encode("utf-8"))


def test_dump_get_body():
    class A:
        def get_body(self):
            return b"Now I am become Death, the destroyer of worlds."

    s = dumps(A())

    assert s.splitlines()[-1] == b"Now I am become Death, the destroyer of worlds."


def test_dump_body_attr():
    class A:
        def __init__(self):
            self.body = b"1234"

    s = dumps(A())

    assert s.splitlines()[-1] == b"1234"

# TODO: error handling, acceptance etc.