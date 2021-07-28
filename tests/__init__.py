"""Unit test package for aioproc."""

import asyncio
from functools import wraps

def async_test(func):
    async def setup_and_run(self, *args, **kwargs):
        if getattr(self, "asyncSetup", None):
            await self.asyncSetup()

        try:
            await func(self)
        finally:
            if getattr(self, "asyncTearDown", None):
                await self.asyncTearDown()

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return asyncio.run(setup_and_run(self, *args, **kwargs))

    return wrapper
