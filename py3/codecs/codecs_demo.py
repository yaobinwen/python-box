"""This file contains examples of using binary sequence types. For the
documentation, see
https://docs.python.org/3.13/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview
This document is referred to as `DOC` in the code.
"""

import unittest


class TestErrorHandlingSchemes(unittest.TestCase):
    def test_error_handling_schemes(self):
        # If `source` is a string and `encoding` is not appropriate, we can
        # specify how the encoding errors should be handled.
        # See https://docs.python.org/3/library/codecs.html#error-handlers for
        # the available schemes.
        s = "ħ"
        encoding = "ascii"

        def _err_handling_scheme_strict():
            self.assertRaises(
                UnicodeEncodeError,
                bytearray,
                source=s,
                encoding=encoding,
                errors="strict",
            )

        _err_handling_scheme_strict()

        def _err_handling_scheme_ignore():
            ba = bytearray(source=s, encoding=encoding, errors="ignore")
            self.assertEqual(len(ba), 0)

        _err_handling_scheme_ignore()

        def _err_handling_scheme_replace():
            replace_char = "?".encode("ascii")
            ba = bytearray(source=s, encoding=encoding, errors="replace")
            self.assertEqual(len(ba), len(replace_char))
            for i in range(len(ba)):
                self.assertEqual(ba[i], replace_char[i])

        _err_handling_scheme_replace()

        def _err_handling_scheme_backslashreplace():
            ba = bytearray(source=s, encoding=encoding, errors="backslashreplace")
            code_point_str = "\\u0127"
            for b, ch in zip(ba, code_point_str):
                self.assertEqual(b, ord(ch))

        _err_handling_scheme_backslashreplace()

        # TODO(ywen): Implement me!
        # surrogateescape
        # xmlcharrefreplace
        # namereplace
        # surrogatepass


if __name__ == "__main__":
    unittest.main()
