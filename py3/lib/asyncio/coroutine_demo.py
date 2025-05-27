"""This file contains examples of using `asyncio` coroutines. For its
documentation, see https://docs.python.org/3.12/library/asyncio-task.html.

This document is referred to as `DOC` in the code.
"""

import asyncio
import unittest


class TestCoroutines(unittest.TestCase):
    def test_creating_and_executing_a_coroutine(self):
        """Test the creation and execution of a coroutine. This test case
        shows that calling a coroutine function only creates a coroutine but
        does not execute it.
        """

        N = 1

        async def incN(n: int) -> int:
            nonlocal N

            N += n
            return N

        # Calling the coroutine function `incN` only returns a coroutine object
        # but does not execute it. `await` must be used to execute the
        # coroutine.
        co = incN(2)

        # Because `co` is not executed, `N` is still 1.
        self.assertEqual(N, 1)

        # Now let's execute the coroutine.
        # In earlier version of Python, we needed to call
        # `asyncio.get_event_loop().run_until_complete(co)` to run the
        # coroutine.
        asyncio.run(co)

        # Because `co` was executed, `N` is now 3.
        self.assertEqual(N, 3)


if __name__ == "__main__":
    """This is the entry point of the program."""
    # Run the main function in the event loop
    unittest.main()
