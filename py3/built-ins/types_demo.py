"""This file contains examples of using binary sequence types. For the
documentation, see
https://docs.python.org/3.13/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview
This document is referred to as `DOC` in the code.
"""

import unittest


class Test_bytearray(unittest.TestCase):
    """Demo code for `bytearray`: `bytearray` objects are a *mutable* counterpart
    to `bytes` objects.
    """

    def test_bytearray(self):
        # Create an empty instance.
        ba = bytearray()
        self.assertEqual(len(ba), 0)

        # If `source` is an integer, it indicates the expected length of the
        # bytearray.
        ba = bytearray(10)
        self.assertEqual(len(ba), 10)
        for b in ba:
            # Every element in the bytearray is zero (i.e., null byte).
            self.assertEqual(b, 0)

        # If `source` is a string but `encoding` is not provided, a `TypeError`
        # will be raised.
        self.assertRaisesRegex(
            TypeError, r"string argument without an encoding", bytearray, source="hello"
        )

        # If `source` is a string and `encoding` is provided, the bytearray is
        # initialized with the encoded string.
        s = "hello"
        ba = bytearray(source=s, encoding="ascii")
        self.assertEqual(len(ba), len(s))
        for index, ch in zip(range(len(s)), s):
            with self.subTest(index=index):
                self.assertEqual(ba[index], ord(ch))

        # If `source` is a string but `encoding` is not appropriate,
        # A string of Unicode characters that cannot be encoded into raw bytes
        # using ASCII.
        s = "ħĕÎÎō"
        encoding = "ascii"
        self.assertRaisesRegex(
            UnicodeEncodeError,
            (
                rf"'{encoding}' codec can't encode characters in "
                r"position \d+-\d+: ordinal not in range\(128\)"
            ),
            bytearray,
            source=s,
            encoding=encoding,
        )

        # If `source` is a string and `encoding` is not appropriate, we can
        # specify how the encoding errors should be handled.
        # See https://docs.python.org/3/library/codecs.html#error-handlers for
        # the available schemes. We only demo a few of them here.
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


if __name__ == "__main__":
    unittest.main()
