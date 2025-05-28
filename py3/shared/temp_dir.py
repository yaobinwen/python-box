# coding: UTF-8

import contextlib
import functools
import pathlib
import shutil
import tempfile

from collections.abc import Callable


def mkdtemp(
    delete: bool = True,
    suffix: str = None,
    prefix: str = None,
    tmpdir: pathlib.Path = None,
) -> Callable:
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwds):
            if tmpdir is not None:
                tmpdir = str(tmpdir)
            d = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=tmpdir)
            try:
                return f(*args, dtemp=pathlib.Path(d), **kwds)
            finally:
                if delete:
                    shutil.rmtree(d, ignore_errors=True)

        return decorated

    return decorator


@contextlib.contextmanager
def dtemp(
    delete: bool = True,
    suffix: str = None,
    prefix: str = None,
    tmpdir: pathlib.Path = None,
):
    if tmpdir is not None:
        tmpdir = str(tmpdir)
    d = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=tmpdir)
    try:
        yield pathlib.Path(d)
    finally:
        if delete:
            shutil.rmtree(d, ignore_errors=True)
