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

    def test_bytearray_empty(self):
        """Test case: `source` is not provided.
        """
        # Create an empty instance.
        ba = bytearray()
        self.assertEqual(len(ba), 0)

    def test_bytearray_integer(self):
        """Test case: `source` is an integer which indicates the expected
        length of the bytearray.
        """
        ba = bytearray(10)
        self.assertEqual(len(ba), 10)
        for b in ba:
            # Every element in the bytearray is zero (i.e., null byte).
            self.assertEqual(b, 0)

        # If provided with zero, it's the same as creating an empty bytearray.
        ba = bytearray(0)
        self.assertEqual(len(ba), 0)

        # If provided a negative integer, it raises `ValueError`.
        self.assertRaisesRegex(ValueError, r"negative count", bytearray, source=-1)

    def test_bytearray_range(self):
        """Test case: `source` is a list of integers.
        """
        # If `source` is a list of integers (0 <= n <= 255), then the bytearray
        # is initialized from the list of integers.
        ba = bytearray(range(256))
        self.assertEqual(len(ba), 256)
        for b, n in zip(ba, range(256)):
            # Every element in the bytearray is the corresponding integer.
            self.assertEqual(b, n)

        # If the given integer is out of range, `ValueError` is raised.
        for n in (-1, 256):
            with self.subTest(n=n):
                self.assertRaisesRegex(
                    ValueError,
                    r"byte must be in range\(0, 256\)",
                    bytearray,
                    source=[n],
                )

    def test_bytearray_str(self):
        """Test case: `source` is a string.
        """
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

    def test_bytearray_buffer(self):
        """Test case: `source` implements the buffer interface.
        """
        # `source` is a bytes object.
        d = b"hello"
        ba = bytearray(source=d)
        self.assertEqual(len(ba), len(d))
        for b1, b2 in zip(ba, d):
            self.assertEqual(b1, b2)

        # `source` is another bytearray.
        ba2 = bytearray(source=ba)
        self.assertEqual(len(ba2), len(ba))
        for b1, b2 in zip(ba, ba2):
            self.assertEqual(b1, b2)

    def test_fromhex(self):
        for string in (
            "4849",
            " 4849",
            "4849 ",
            "48 49",
            " 48 49",
            "48 49 ",
            " 48 49 ",
            "\t4849",
            "4849\t",
            "48\t49",
            "\t48\t49",
            "48\t49\t",
            "\t48\t49\t",
        ):
            with self.subTest(string=string):
                ba = bytearray.fromhex(string)
                self.assertEqual(ba[0], 0x48)
                self.assertEqual(ba[1], 0x49)

    def test_hex(self):
        source = [0x01, 0x02, 0x03, 0x04, 0x05]

        for sep, bytes_per_sep, expected in [
            ("_", 0, "0102030405"),
            ("_", 1, "01_02_03_04_05"),
            # Interesting... So it looks like the separator is applied from the
            # last byte back to the first byte.
            ("_", 2, "01_0203_0405"),
            ("_", 3, "0102_030405"),
            ("_", 4, "01_02030405"),
            # When `bytes_per_sep` is the same as the number of the bytes, it's
            # essentially equivalent to `bytes_per_sep == 0`.
            ("_", 5, "0102030405"),
            # When `bytes_per_sep` is more than the number of the bytes, it's
            # essentially ineffective.
            ("_", 6, "0102030405"),
        ]:
            with self.subTest(sep=sep, bytes_per_sep=bytes_per_sep):
                b = bytearray(source=source)
                self.assertEqual(b[0], 0x01)
                self.assertEqual(b[4], 0x05)
                s = b.hex(sep=sep, bytes_per_sep=bytes_per_sep)
                self.assertEqual(s, expected)

    def test_slices(self):
        b = bytearray(b'0123')

        # If we only get one particular element in bytearray, it is an integer.
        self.assertIsInstance(b[0], int)
        self.assertEqual(b[0], ord('0'))

        # If we get a range of elements in bytearray, even if it has only one
        # element, it's still a bytearray.
        self.assertIsInstance(b[0:1], bytearray)
        self.assertEqual(len(b[0:1]), 1)
        self.assertEqual(b[0:1].hex(), "30")

    def test_convert_to_list(self):
        b = bytearray(b'0123')
        # Convert b into a list of integers.
        n = list(b)
        expected = [ord('0'), ord('1'), ord('2'), ord('3')]
        self.assertListEqual(n, expected)


if __name__ == "__main__":
    unittest.main()
