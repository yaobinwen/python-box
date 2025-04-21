"""This file contains examples of using `asyncio` runners. For its
documentation, see https://docs.python.org/3/library/asyncio-runner.html.

This document is referred to as `DOC` in the code.
"""

import asyncio
import unittest


class TestRunners(unittest.TestCase):
    async def _inc(self, *, n: int) -> int:
        """Increment the number by 1."""
        return n + 1

    def test_run(self):
        """Test the `asyncio.run()` function."""
        # `asyncio.run()` accepts a coroutine object, so we should pass the
        # result of calling `self._inc()`, not the function itself.
        coro = self._inc(n=1)
        result = asyncio.run(coro)
        # Check if the result is 2
        self.assertEqual(result, 2)


if __name__ == "__main__":
    """This is the entry point of the program."""
    # Run the main function in the event loop
    unittest.main()
