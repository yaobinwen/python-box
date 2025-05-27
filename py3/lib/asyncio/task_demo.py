"""This file contains examples of using `asyncio` coroutines. For its
documentation, see https://docs.python.org/3.12/library/asyncio-task.html.

This document is referred to as `DOC` in the code.
"""

import asyncio
import signal
import time
import unittest


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

    def test_creating_does_not_run_a_task(self):
        """Show that creating a task does not run it until the task is awaited."""
        B = 1

        async def incB(n: int) -> int:
            nonlocal B

            # We don't start to execute the increment immediately.
            time.sleep(0.5)

            B += n
            return B

        # Calling the coroutine function `incB` only returns a coroutine object
        # but does not execute it.
        co = incB(2)

        # `asyncio.create_task` starts to execute the coroutine immediately but
        # its a concurrent execution so it doesn't block the caller's thread.
        event_loop = asyncio.new_event_loop()
        t = event_loop.create_task(co)

        # Because `co` is not executed, `B` is still 1.
        self.assertEqual(B, 1)

        # We wait for at most 3 seconds for the task to complete.
        async_sleep_seconds = 0.1
        timeout_in_seconds = 3
        iterations = int(timeout_in_seconds / async_sleep_seconds)
        timed_out = True
        for i in range(iterations):
            event_loop.run_until_complete(asyncio.sleep(async_sleep_seconds))
            if B == 3:
                timed_out = False
                break

        self.assertFalse(timed_out, "Task did not complete in time.")
        self.assertEqual(B, 3)

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

            await asyncio.sleep(5)
            events.append(2)

            task.cancel()
            events.append(3)

            await asyncio.sleep(5)
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
