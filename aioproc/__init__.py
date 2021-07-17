"""Top-level package for aioproc."""

__author__ = """Aaron Yang"""
__email__ = 'code@jieyu.ai'
__version__ = '0.1.0'


"""Main module."""
import functools
import functools
from typing import List, Tuple
import asyncio
import shlex
import sys
import fire

async def _echo(stream):
    while True:
        line = await stream.readline()
        line = line.decode("utf-8")
        if not line:
            break
        print(line)

def _async_wrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper

class OutputCollector:
    def __init__(self, encoding="utf-8"):
        self.encoding=encoding
        self.buffer = []

    async def __call__(self, stream):
        while True:
            line = await stream.readline()
            line = line.decode(self.encoding)
            if not line:
                break
            self.buffer.append(line.rstrip("\n"))
    
def expose(funcs:dict):
    """expose `funcs` so that it can be called by `aiofunc`

    each pair in `funcs` defines a `name` (alias) and a function, which will be actually called when `name` is invoked
    Args:
        funcs: name and function
    """
    _exposed = {}

    for name ,func in funcs.items():
        if asyncio.iscoroutinefunction(func):
            _exposed[name] = _async_wrap(func)
        else:
            _exposed[name] = func

    fire.Fire(_exposed)

async def aiofunc(package: str, func: str, args:Tuple=None, kwargs:dict=None, encoding='utf-8', delay=0)->Tuple[List, List]:
    """invoke a python function(which defined in `package.__main__`) in another process, and collects output(stdout, stderr)

    args and kwargs should be serializable

    Args:
        package (str): [description]
        func (str): [description]
        args ([type], optional): [description]. Defaults to None.
        kwargs ([type], optional): [description]. Defaults to None.
        encoding (str, optional): [description]. Defaults to 'utf-8'.
        delay (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: [description]
    """
    if args:
        args = [f"'{arg}'" for arg in args]
    else:
        args = []
    if kwargs:
        kwargs = [f"--{key}='{value}'" for key, value in kwargs.items() if kwargs]
    else:
        kwargs = []
    
    cmds = [sys.executable, "-m", package, func, *args, *kwargs]
    out, err = OutputCollector(), OutputCollector()

    await aioprocess(*cmds, stdout_handler=out, stderr_handler=err)
    await asyncio.sleep(delay)

    return out.buffer, err.buffer

async def aioprocess(*cmds, stdout_handler=_echo, stderr_handler=_echo):
    """execute cmds in asyncio process, and echo it's stdout/stderr

    Examples:
        >>> aioprocess("ls")
        >>> aioprocess("ping -c 10 www.baidu.com")
        >>> aioprocess("ping", "-c", "10", "www.baidu.com")
        >>> aioprocess("python -m http.server")
    Args:
        cmds ([type]): command line
        stdout_handler ([type], optional): [description]. Defaults to echo.
        stderr_handler ([type], optional): [description]. Defaults to echo.
    """
    if len(cmds) == 1 and isinstance(cmds[0], str):
        cmds = shlex.split(cmds[0])
        
    proc = await asyncio.create_subprocess_exec(
        *cmds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    if stdout_handler:
        asyncio.ensure_future(stdout_handler(proc.stdout))
    if stderr_handler:
        asyncio.ensure_future(stderr_handler(proc.stderr))

    await proc.wait()

