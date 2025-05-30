"""This file contains examples of using `io`. For its documentation, see
https://docs.python.org/3/library/io.html
This document is referred to as `DOC` in the code.
"""

import collections
import errno
import functools
import io
import os
import pathlib
import shutil
import sys
import tempfile
import unittest


def mkdtemp(prefix, delete=True, tmpdir=None):
    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            d = tempfile.mkdtemp(prefix=prefix, dir=tmpdir)
            try:
                return f(*args, dtemp=pathlib.Path(d), **kwds)
            finally:
                if delete:
                    shutil.rmtree(d, ignore_errors=True)

        return wrapper

    return wrap


DTEMP_PREFIX = "tmp.io_demo."


class Test_DEFAULT_BUFFER_SIZE(unittest.TestCase):
    def test(self):
        S = io.DEFAULT_BUFFER_SIZE
        self.assertIsInstance(S, int)
        self.assertTrue(S > 0)


class Test_text_encoding(unittest.TestCase):
    """Generally speaking, `text_encoding` tries to return an appropriate
    encoding that the I/O functions can use. It also issues the `EncodingWarning`
    if asked to do so.
    """

    def test_encoding_not_None(self):
        """Test case: `encoding` is not None."""
        # When `encoding` is not None, it returns whatever is given to
        # `encoding`.
        encoding = io.text_encoding("something")
        self.assertEqual(encoding, "something")

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_encoding_None(self, dtemp):
        """Test case: `encoding` is None."""
        # This test requires `sys.flags.warn_default_encoding` be set to True.
        # Run the Python interpreter with `-X warn_default_encoding` to enable
        # the warning.
        self.assertTrue(bool(sys.flags.warn_default_encoding))

        utf8_mode = bool(sys.flags.utf8_mode)

        # When `encoding` is None, it's usually because of the legacy code that
        # didn't (or couldn't) specify the encoding. In this case,
        # `io.text_encoding` returns the appropriate string to indicate the
        # preferred encoding.
        encoding = None
        encoding = io.text_encoding(encoding)

        if utf8_mode:
            # `encoding` being `utf-8` means always using UTF-8.
            self.assertEqual(encoding, "utf-8")
        else:
            # `encoding` being `locale` means using the encodeing that's
            # specified in the current locale.
            self.assertEqual(encoding, "locale")

        ftmp = dtemp / "test.txt"
        ftmp.write_text("test_encoding_None", encoding="utf-8")

        with io.open(str(ftmp), encoding=encoding) as fh:
            fh.read()


class TestFileIO(unittest.TestCase):
    def _set_up(self, *, dtemp, filename):
        content = "hello"
        ftmp = dtemp / filename
        ftmp.write_text(content, encoding="utf-8")
        return (ftmp, content)

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_filename_in_bytes(self, dtemp):
        ftmp, content = self._set_up(dtemp=dtemp, filename="test1.txt")

        # Convert the file path from a string into an array of bytes.
        fpath_in_bytes = str(ftmp).encode("utf-8")
        f = io.FileIO(fpath_in_bytes, mode="r", closefd=True, opener=None)

        # `FileIO` is a *binary* stream so even if we only specified 'r' for
        # `mode`, the mode `b` is still implied.
        self.assertEqual(f.mode, "rb")
        self.assertEqual(f.name, fpath_in_bytes)

        f.close()

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_filename_in_str(self, dtemp):
        ftmp, content = self._set_up(dtemp=dtemp, filename="test2.txt")

        fpath_in_str = str(ftmp)
        f = io.FileIO(fpath_in_str, mode="r", closefd=True, opener=None)

        # `FileIO` is a *binary* stream so even if we only specified 'r' for
        # `mode`, the mode `b` is still implied.
        self.assertEqual(f.mode, "rb")
        self.assertEqual(f.name, fpath_in_str)

        f.close()

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_filename_fd(self, dtemp):
        ftmp, content = self._set_up(dtemp=dtemp, filename="test3.txt")

        buffered_reader = ftmp.open(mode="rb")
        f = io.FileIO(buffered_reader.fileno(), mode="r", closefd=True, opener=None)

        # `FileIO` is a *binary* stream so even if we only specified 'r' for
        # `mode`, the mode `b` is still implied.
        self.assertEqual(f.mode, "rb")
        self.assertEqual(f.name, buffered_reader.fileno())

        f.close()
        try:
            # If we don't call `buffered_reader.close()`, Python will issue
            # `ResourceWarning: unclosed file <_io.BufferedReader ...>`. However,
            # because closing on `f` will close the underlying file descriptor
            # (because `closefd=True`. Therefore, when we close), calling
            # `buffered_reader.close()` will raise `OSError` of `EBADF`. So we
            # need to call it (in order to fix the `ResourceWarning` but also
            # catch the OSError so it doesn't crash the program.
            buffered_reader.close()
        except OSError as e:
            if e.errno != errno.EBADF:
                raise

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_closefd_True(self, dtemp):
        """Test case: `closefd=True`"""
        ftmp, content = self._set_up(dtemp=dtemp, filename="test_closefd_True.txt")

        buffered_reader = ftmp.open(mode="rb")
        f = io.FileIO(buffered_reader.fileno(), mode="r", closefd=True, opener=None)

        # Because `closefd=True`, closing `f` will also close the file
        # descriptor so `buffered_reader` no longer points to a valid file
        # descriptor. However, from `buffered_reader`'s point of view, the
        # file is still not closed.
        # With that said, `closefd=True` is more suitable for the situation of
        # transferring the management of the underlying file descriptor from
        # the file object to this `FileIO` object, so the file descriptor is
        # only closed by the `FileIO` object.
        f.close()
        self.assertFalse(buffered_reader.closed)
        self.assertRaisesRegex(
            OSError,
            rf"\[Errno {errno.EBADF}\] Bad file descriptor",
            buffered_reader.close,
        )

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_closefd_False(self, dtemp):
        """Test case: `closefd=False`"""
        ftmp, content = self._set_up(dtemp=dtemp, filename="test_closefd_False.txt")

        buffered_reader = ftmp.open(mode="rb")
        f = io.FileIO(buffered_reader.fileno(), mode="r", closefd=False, opener=None)

        # Because `closefd=False`, closing `f` will not close the file descriptor
        # so `buffered_reader` will still point to a valid file descriptor that
        # should be closed in order to prevent `ResourceWarning`.
        f.close()
        self.assertFalse(buffered_reader.closed)
        buffered_reader.close()
        self.assertTrue(buffered_reader.closed)

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_opener_not_None(self, dtemp):
        """Test case: `opener` is not None."""
        ftmp, content = self._set_up(dtemp=dtemp, filename="test_opener_not_None.txt")

        def _opener(name, flags):
            self.assertEqual(name, ftmp)
            self.assertIsInstance(flags, int)

            fd = os.open(path=name, flags=flags)
            return fd

        f = io.FileIO(ftmp, mode="r", closefd=True, opener=_opener)

        # Fix `ResourceWarning`.
        f.close()

    @mkdtemp(prefix=DTEMP_PREFIX)
    def test_fd_not_inheritable(self, dtemp):
        """Test case: returned file descriptor is not inheritable."""
        ftmp, content = self._set_up(
            dtemp=dtemp, filename="test_fd_not_inheritable.txt"
        )
        f = io.FileIO(ftmp, mode="r", closefd=True, opener=None)
        # The file descriptor is not inheritable by default.
        self.assertFalse(os.get_inheritable(f.fileno()))
        f.close()


class TestBytesIO(unittest.TestCase):
    def test_BytesIO_initial_bytes(self):
        """Test `BytesIO`'s constructor."""
        # No initial bytes.
        s = io.BytesIO()
        self.assertEqual(s.getvalue(), b"")

        # Some initial bytes.
        s = io.BytesIO(initial_bytes=b"abc")
        self.assertEqual(s.getvalue(), b"abc")

    def test_getbuffer(self):
        """Test `getbuffer` that returns a readable and writable view"""
        initial_bytes = b"012345"
        s = io.BytesIO(initial_bytes=initial_bytes)
        view = s.getbuffer()

        # `view[n]` returns the binary value of the (n-1)th byte.
        self.assertEqual(view[0], initial_bytes[0])
        self.assertEqual(view[len(initial_bytes) - 1], initial_bytes[-1])

        # `view[n:m]` returns an array of bytes.
        self.assertEqual(view[0:1], initial_bytes[0:1])
        self.assertEqual(view[2:4], initial_bytes[2:4])

        # Write via a view.
        view[0] = ord(b"a")
        value = s.getvalue()
        self.assertEqual(value, b"a12345")

        view[1:] = b"bcdef"
        value = s.getvalue()
        self.assertEqual(value, b"abcdef")

    def test_getvalue(self):
        initial_bytes = b"abc"
        s = io.BytesIO(initial_bytes=initial_bytes)
        self.assertEqual(s.getvalue(), initial_bytes)

    def test_read1(self):
        initial_bytes = b"abc"

        def _read1(size):
            s = io.BytesIO(initial_bytes=initial_bytes)
            return s.read1(size)

        read1_test_case = collections.namedtuple(
            "read1_test_case", ["size", "expected"]
        )
        test_cases = [
            # If `size` is None or negative, read until EOF.
            read1_test_case(size=None, expected=initial_bytes),
            read1_test_case(size=-1, expected=initial_bytes),
            # If `size` is zero, read nothing.
            read1_test_case(size=0, expected=b""),
            # If `size` is positive but not longer than the length of the data,
            # read the specified number of bytes.
            read1_test_case(size=1, expected=chr(initial_bytes[0]).encode("utf-8")),
            read1_test_case(size=3, expected=initial_bytes[0:3]),
            read1_test_case(size=30, expected=initial_bytes),
        ]

        for tc in test_cases:
            with self.subTest(size=tc.size):
                r = _read1(tc.size)
                self.assertEqual(r, tc.expected)

    def test_readinto1(self):
        initial_bytes = b"hello, world"

        def _readinto1(buf_size):
            # Allocate a bytearray of the specified size. This will be the
            # maximal size that `readinto1` can write to the bytearray.
            b = bytearray(buf_size)
            s = io.BytesIO(initial_bytes=initial_bytes)
            num = s.readinto1(b)
            return num, b

        expected_30 = bytearray(30)
        expected_30[0 : len(initial_bytes)] = initial_bytes

        readinto1_test_case = collections.namedtuple(
            "readinto1_test_case", ["buf_size", "expected_num", "expected_bytes"]
        )
        test_cases = [
            # If `buf_size` is zero, read into nothing because there is no space
            # for the target bytearry to hold anything.
            readinto1_test_case(buf_size=0, expected_num=0, expected_bytes=b""),
            # If `buf_size` is positive but smaller than the length of the data,
            # then read as many bytes as possible.
            readinto1_test_case(buf_size=1, expected_num=1, expected_bytes=b"h"),
            readinto1_test_case(buf_size=3, expected_num=3, expected_bytes=b"hel"),
            # If `buf_size` is large enough to hold all the data, then read all
            # of them.
            readinto1_test_case(
                buf_size=30, expected_num=len(initial_bytes), expected_bytes=expected_30
            ),
        ]

        for tc in test_cases:
            with self.subTest(buf_size=tc.buf_size):
                num_read, b = _readinto1(buf_size=tc.buf_size)
                self.assertEqual(num_read, tc.expected_num)
                self.assertEqual(b, tc.expected_bytes)


class TestBufferedReader(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


class TestBufferedWriter(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


class TestBufferedRandom(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


class TestBufferedRWPair(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


class TestTextIOWrapper(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


class TestStringIO(unittest.TestCase):
    # TODO(ywen): Implement me!
    pass


if __name__ == "__main__":
    unittest.main()
