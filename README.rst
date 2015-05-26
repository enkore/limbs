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

Line endings in the header can be UNIX style (\n, preferred) or Windows style (\r\n).
Windows style endings are always converted to UNIX style endings when reading, and only UNIX
style endings are written.

Primary APIs are ``dump``, ``dumps``, ``load`` and ``loads``.
