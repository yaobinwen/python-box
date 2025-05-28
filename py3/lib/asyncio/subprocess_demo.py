"""This file contains examples of using `asyncio` coroutines. For its
documentation, see https://docs.python.org/3/library/asyncio-subprocess.html.

This document is referred to as `DOC` in the code.
"""

import asyncio
import errno
import os
import resource
import unittest

from shared import temp_dir


class TestSubprocess(unittest.TestCase):
    def test_create_subprocess_exec(self):
        async def _echo():
            p = await asyncio.create_subprocess_exec(
                "echo",
                "hello",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await p.wait()

            stdout_text = ""
            stderr_text = ""
            if p.stdout:
                stdout_bytes = await p.stdout.read()
                stdout_text = stdout_bytes.decode().strip()
            if p.stderr:
                stderr_bytes = await p.stderr.read()
                stderr_text = stderr_bytes.decode().strip()

            return p.returncode, stdout_text, stderr_text

        rc, stdout_text, stderr_text = asyncio.run(_echo())
        self.assertEqual(rc, 0)
        self.assertEqual(stdout_text, "hello")
        self.assertEqual(stderr_text, "")

    def test_create_subprocess_exec_errors(self):
        """Show the errors that `asyncio.create_subprocess_exec` can raise."""

        async def _file_not_found_error():
            # `fake_echo` doesn't exist so `create_subprocess_exec` will throw
            # `FileNotFoundError`.
            p = await asyncio.create_subprocess_exec("fake_echo", "hello")
            await p.wait()

        async def _permission_error():
            with temp_dir.dtemp(prefix="asyncio.subprocess_demo") as dtemp:
                f = dtemp / "hello.txt"
                f.touch()

                # `f` is not an executable file so `create_subprocess_exec`
                # will throw `PermissionError`.
                p = await asyncio.create_subprocess_exec(str(f))
                await p.wait()

        async def _value_error():
            # `shell` must be `False` for `create_subprocess_exec` so
            # `create_subprocess_exec` will throw `ValueError`.
            p = await asyncio.create_subprocess_exec("ls", "/", shell=True)
            await p.wait()

        async def _timeout_error():
            p = await asyncio.create_subprocess_exec("sleep", "1")
            await asyncio.wait_for(p.wait(), timeout=0.1)

        async def _connection_reset_error():
            # Set `stdin=asyncio.subprocess.PIPE` to accept input.
            p = await asyncio.create_subprocess_exec(
                "true", stdin=asyncio.subprocess.PIPE
            )
            # But by waiting for `p.wait()`, the command already finishes.
            await p.wait()

            # We don't write data to stdin until the command finishes, so the
            # pipe was already closed and `drain()` will raise
            # `ConnectionResetError`.
            p.stdin.write(b"hello")
            await p.stdin.drain()

        async def _os_error_two_many_files():
            # Figure out the number of already open file descriptors.
            opened_fds = len(os.listdir("/proc/self/fd"))

            # Get current limits so we can restore them later.
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)

            num_of_more = 4

            # Set the soft limit to simulate exhaustion.
            resource.setrlimit(
                resource.RLIMIT_NOFILE, (opened_fds + num_of_more, hard_limit)
            )

            # Open more file to trigger the "Too many open files" error.
            fds = []
            more_files_opened = False
            try:
                for _ in range(num_of_more):
                    fds.append(open("/dev/null"))

                more_files_opened = True

                # Because we have exhausted all of the file descriptors that
                # are allowed to be opened, launching a new subprocess will
                # raise `OSError` with "Too many open files".
                await asyncio.create_subprocess_exec("echo", "hello")
            except OSError:
                if not more_files_opened:
                    # Make sure the OSError was caused by
                    # `create_subprocess_exec`.
                    raise RuntimeError(
                        "We should be able to open more files "
                        "without triggering OSError but somehow we failed."
                    ) from None
                else:
                    # Otherwise, re-raise the OSError.
                    raise
            finally:
                for f in fds:
                    f.close()
                resource.setrlimit(resource.RLIMIT_NOFILE, (soft_limit, hard_limit))

        async def _os_error_bad_file_descriptor():
            try:
                await asyncio.create_subprocess_exec(
                    "echo",
                    "hello",
                    # Not a valid Stream or None or PIPE
                    stdin=1234567890,
                )
            except OSError as e:
                if e.errno != errno.EBADF:
                    # If the OSError is not about "bad file descriptor",
                    # something went wrong and we should report it.
                    raise RuntimeError(
                        f"errno {errno.EBADF} was expected but got {e.errno}"
                    ) from None
                else:
                    # Otherwise, we re-raise the OSError.
                    raise

        async def _cancel_error():
            p = await asyncio.create_subprocess_exec("sleep", "5")
            t = asyncio.create_task(p.wait())
            t.cancel()

            await t

        self.assertRaises(FileNotFoundError, asyncio.run, _file_not_found_error())
        self.assertRaises(PermissionError, asyncio.run, _permission_error())
        self.assertRaises(ValueError, asyncio.run, _value_error())
        self.assertRaises(asyncio.TimeoutError, asyncio.run, _timeout_error())
        self.assertRaises(ConnectionResetError, asyncio.run, _connection_reset_error())
        self.assertRaises(OSError, asyncio.run, _os_error_two_many_files())
        self.assertRaises(OSError, asyncio.run, _os_error_bad_file_descriptor())
        self.assertRaises(asyncio.CancelledError, asyncio.run, _cancel_error())

        # TODO(ywen): RuntimeError, but not sure how to trigger it.

    def test_create_subprocess_exec_no_CalledProcessError(self):
        """Show that `asyncio.create_subprocess_exec` does not raise
        `CalledProcessError` as `subprocess` does.
        """

        async def _ls_invalid_option():
            p = await asyncio.create_subprocess_exec(
                "ls", "--shout", stderr=asyncio.subprocess.DEVNULL
            )
            await p.wait()

        try:
            asyncio.run(_ls_invalid_option())
        except Exception:
            self.fail("The failure of the program itself should not raise any error")


if __name__ == "__main__":
    """This is the entry point of the program."""
    # Run the main function in the event loop
    unittest.main()
