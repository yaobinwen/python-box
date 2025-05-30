"""This file contains examples of using `asyncio` coroutines. For its
documentation, see https://docs.python.org/3.12/library/asyncio-task.html.

This document is referred to as `DOC` in the code.
"""

import asyncio
import functools
import io
import math
import signal
import time
import unittest

from collections.abc import Callable


class TestTasks(unittest.TestCase):
    def test_creating_without_a_running_loop(self):
        """Show that a task must be created in a running event loop."""
        A = 1

        async def incA(n: int) -> int:
            nonlocal A
            A += n
            return A

        try:
            # At this moment, we haven't created a running event loop so we
            # can't create tasks yet.
            asyncio.create_task(incA(2))
        except RuntimeError as e:
            self.assertIn("no running event loop", str(e))

        # Because we didn't run the task successfully, `A` is still 1.
        self.assertEqual(A, 1)

        # In order to create a task, we need to have a running event loop first.
        event_loop = asyncio.new_event_loop()
        t = event_loop.create_task(incA(2))
        event_loop.run_until_complete(t)
        self.assertEqual(A, 3)

    def _wait_for(
        self,
        *,
        check: Callable,
        sync_sleep: bool = True,
        sleep_s: float = 0.1,
        timeout_s: float = 3,
        event_loop=None,
    ):
        iterations = math.ceil(timeout_s / sleep_s)
        timed_out = True
        for i in range(iterations):
            if sync_sleep:
                time.sleep(sleep_s)
            else:
                event_loop.run_until_complete(asyncio.sleep(sleep_s))
            if check():
                timed_out = False
                break

        return timed_out

    def test_creating_does_not_run_a_task(self):
        """Show that creating a task does not run the wrapped coroutine unless
        it's awaited.
        """

        class _Demo:
            def __init__(self):
                self.strbuf = io.StringIO()

            async def update_str(self, N: int):
                for i in range(0, N):
                    self.strbuf.write(str(i))
                    # Sleep a bit so this method can't finish that quickly.
                    await asyncio.sleep(0.5)

        d = _Demo()
        self.assertEqual(d.strbuf.getvalue(), "")

        # Calling the coroutine function `incB` only returns a coroutine object
        # but does not execute it.
        coro = d.update_str(N=3)

        # `asyncio.create_task` starts to execute the coroutine immediately but
        # its a concurrent execution so it doesn't block the caller's thread.
        event_loop = asyncio.new_event_loop()
        t = event_loop.create_task(coro)

        def _check_completion(d: _Demo, expected_value: str):
            return d.strbuf.getvalue() == expected_value

        # Wait for 3 seconds synchronously without running any event loop.
        # As a result, the `update_str` couldn't be completed.
        timed_out = self._wait_for(
            check=functools.partial(_check_completion, d=d, expected_value="012"),
            sync_sleep=True,
            event_loop=None,
        )
        self.assertTrue(timed_out)
        self.assertEqual(d.strbuf.getvalue(), "")

        # Wait for 3 second asynchronously. Because the event loop runs, it
        # also runs `update_str` so it can complete.
        timed_out = self._wait_for(
            check=functools.partial(_check_completion, d=d, expected_value="012"),
            sync_sleep=False,
            event_loop=event_loop,
        )
        self.assertFalse(timed_out)
        self.assertEqual(d.strbuf.getvalue(), "012")


    def test_cancel_subprocess(self):
        """Show how to cancel a subprocess."""
        event_loop = asyncio.new_event_loop()

        canceled = False
        events = []

        async def _sleep(n: int):
            p = None
            try:
                p = await asyncio.create_subprocess_exec("sleep", str(n))
                await p.wait()
            except asyncio.CancelledError:
                p.send_signal(signal.SIGINT)

                nonlocal canceled, events
                canceled = True
                events.append(4)

        async def _main():
            nonlocal event_loop, events

            task = event_loop.create_task(_sleep(300))
            events.append(1)

            await asyncio.sleep(1)
            events.append(2)

            task.cancel()
            events.append(3)

            await asyncio.sleep(1)
            events.append(5)

        event_loop.run_until_complete(_main())

        self.assertTrue(canceled, "Task was not canceled as expected.")
        self.assertListEqual(
            events, [1, 2, 3, 4, 5], "Events did not occur in the expected order."
        )


if __name__ == "__main__":
    """This is the entry point of the program."""
    # Run the main function in the event loop
    unittest.main()
