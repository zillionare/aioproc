#!/usr/bin/env python
"""Tests for `aioproc` package."""

import asyncio
from tests import async_test
from aioproc import aiofunc, aioprocess
import unittest


class OutputCollector:
    def __init__(self):
        self.buffer = []

    async def __call__(self, stream):
        while True:
            line = await stream.readline()
            line = line.decode("utf-8")
            if not line:
                break
            self.buffer.append(line.rstrip())


class TestAioproc(unittest.TestCase):
    @async_test
    async def test_aioproc(self):
        collector = OutputCollector()
        await aioprocess("ping -c 1 www.baidu.com", stdout_handler=collector)
        self.assertTrue("1 packets transmitted" in "".join(collector.buffer))

        collector = OutputCollector()
        await aioprocess("ping", "-c", "1", "www.baidu.com", stdout_handler=collector)
        self.assertTrue("1 packets transmitted" in "".join(collector.buffer))

        collector = OutputCollector()
        await aioprocess("ls", stdout_handler=collector, stderr_handler=None)
        await asyncio.sleep(1)
        self.assertTrue("aioproc" in collector.buffer)

    @async_test
    async def test_aiofunc(self):
        out, err = await aiofunc(
            "aioproc", "echo", args=("echo",), kwargs={"second": 2}, delay=2
        )
        self.assertListEqual(["echo", "second=2"], out)
        self.assertEqual(0, len(err))

        out, err = await aiofunc(
            "aioproc", "async_echo", args=("async_echo",), kwargs={"second": 2}, delay=2
        )
        self.assertListEqual(["async_echo", "second=2"], out)
        self.assertEqual(0, len(err))

        out, err = await aiofunc(
            "aioproc", "async_echo", args=("position only",), delay=2
        )
        self.assertListEqual(["position only", "second=0"], out)
        self.assertEqual(0, len(err))
