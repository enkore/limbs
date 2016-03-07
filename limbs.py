from itertools import chain
import keyword
import inspect
import io


"""
limbs
=====

like mime, but simpler - a simple, human-readable file format

Simple I/O to flat text files with a header (composed of fields) and a body (arbitrary bytes).
Ideal for no-hassle storage of some metadata and some large data that doesn't fit nicely into
things like JSON (which becomes really hard to edit in a text editor if there's a 2 MB blob of
numbers somewhere in it).

While the general format is the same as MIME/"internet messages" and most if not all "internet
messages" can be parsed by this module there are a few distinctions. For starters the header
is always UTF-8 encoded (which doesn't clash with the 7-bit-ASCII-padded-to-bytes used by
internet messages). Field names are mangled to Python identifiers by stripping surrounding
whitespace and dashes, turning them all lower case, replacing dashes (-) with underscores (_)
and appending another underscore if the result is a reserved Python keyword.
If the result of this is not a valid Python identifier, the field name is invalid.

When writing files from objects this translation is reversed (underscores replaced with dashes,
surrounding dashes are removed and the result is title-cased).

Values are simple strings.

The optional body of a file is, in contrast to the header, not UTF-8, but rather treated as
a byte string. If the body is text-like usage of UTF-8 is strongly advised.

Line endings in the header can be UNIX style (\\n, preferred) or Windows style (\\r\\n).
Windows style endings are always converted to UNIX style endings when reading, and only UNIX
style endings are written.

Primary APIs are dump, dumps, load and loads.
"""

ENCODING = "utf-8"


class _LimbsObject:
    def process_body(self, fp):
        self.body = fp.read()


def convert_bool(value):
    value = value.lower()
    if value in ["0", "no", "false"]:
        return False
    elif value in ["1", "yes", "true"]:
        return True
    raise ValueError("Expected boolean value, but '%s' not in 0, 1, no, yes, false, true." % value)


CONVERSIONS = {
    "bool": convert_bool,
    "int": int,
}


def convert_value(value, conversion):
    if not conversion:
        return value
    if conversion in CONVERSIONS:
        return CONVERSIONS[conversion](value)
    return conversion(value)


def decode(bytes):
    return bytes.decode(ENCODING).replace("\r\n", "\n")


def decoded(iterable_of_bytes):
    for bytes in iterable_of_bytes:
        yield decode(bytes)


def pythonize(identifier):
    identifier = identifier.strip(" \t-")
    identifier = identifier.replace("-", "_")
    identifier = identifier.lower()
    if not identifier.isidentifier():
        raise ValueError("Invalid field name: '" + identifier + "'")
    if keyword.iskeyword(identifier):
        identifier += "_"
    return identifier


def get_instance_of(class_or_instance):
    if inspect.isclass(class_or_instance):
        return class_or_instance()
    return class_or_instance


def get_indentation_length(line):
    return len(line) - len(line.lstrip(" \t"))


def is_next_line_indented(file_like):
    next_bytes = file_like.peek(1)
    return next_bytes and next_bytes[0] in b" \t"


def read_continued_field(file_like, value="", indentation=None):
    if not is_next_line_indented(file_like):
        return value
    line = file_like.readline().decode(ENCODING)
    if not indentation:
        indentation = get_indentation_length(line)
    line = line[indentation:]
    return read_continued_field(file_like, value + line, indentation)


def read_field(current_line, file_like, key_transform):
    key, value = current_line.split(":", maxsplit=1)
    value += read_continued_field(file_like)
    value = value.strip()
    key = key_transform(pythonize(key))
    return key, value


def read_body(obj, file_like):
    if hasattr(obj, "process_body"):
        obj.process_body(file_like)


def load(file_like, load_into=_LimbsObject, key_transform=lambda s: s):
    """
    Load limbs-like file, creating or modifying an object.

    If the object doesn't have a process_body method, the body is discarded.

    :param file_like: A file-like object meeting BufferedReader requirements
    :param load_into: Either a class (a new object is created) or an object (returned with attributes set)
    :return: Either a new instance of load_into or load_into
    """
    obj = get_instance_of(load_into)
    conversions = getattr(obj, "_limbs_convert", {})

    for line in decoded(file_like):
        if line == "\n":
            break  # header ended

        key, value = read_field(line, file_like, key_transform)
        try:
            value = convert_value(value, conversions.get(key, None))
        except ValueError as ve:
            raise ValueError("Could not parse value for field '%s'" % key) from ve
        setattr(obj, key, value)

    read_body(obj, file_like)

    return obj


def limbize(identifier):
    identifier = identifier.replace("_", "-")
    identifier = identifier.strip("-")
    identifier = identifier.title()
    return identifier


def indent_continued_field(value):
    return "\n ".join(value.splitlines())


def get_properties(obj):
    # meh
    for property, _ in inspect.getmembers(obj.__class__, inspect.isdatadescriptor):
        if property.startswith("__"):
            continue
        yield property, getattr(obj, property)


def get_object_fields(obj):
    fields = chain(
        vars(obj).items(),
        get_properties(obj)
    )
    fields = filter(lambda kv: not kv[0].startswith("_"), fields)
    return sorted(fields, key=lambda kv: limbize(kv[0]))


def get_object_body(obj):
    if hasattr(obj, "get_body"):
        return obj.get_body()
    if hasattr(obj, "body"):
        return obj.body


def write_field(key, value, file_like):
    key = limbize(key)
    file_like.write(key.encode(ENCODING))
    file_like.write(b": ")
    file_like.write(indent_continued_field(str(value)).encode(ENCODING))
    file_like.write(b"\n")


def write_body(obj, file_like):
    body = get_object_body(obj)
    if body:
        file_like.write(b"\n")
        file_like.write(body)


def dump(obj, file_like):
    """
    Dump an object to a file-like binary stream.

    If the object has a list attribute ``_limbs_ignore`` those attributes are ignored. The field
    ``body`` is always ignored, because it is used as the body, if it exists. In that case it must
    be ``bytes`` or compatible. If the method ``get_body`` exists it is called and the return value
    used instead.
    """
    ignore = ["body"]
    if hasattr(obj, "_limbs_ignore"):
        ignore += obj._limbs_ignore

    for key, value in get_object_fields(obj):
        if key in ignore:
            continue
        write_field(key, value, file_like)

    write_body(obj, file_like)


def loads(byte_string, load_into=_LimbsObject):
    """
    Like load, but load data from a byte string instead.
    """
    return load(io.BufferedReader(io.BytesIO(byte_string)), load_into)


def dumps(obj):
    """
    Like dump, but returning bytes containing encoded data.
    """
    ss = io.BytesIO()
    dump(obj, ss)
    return ss.getvalue()
