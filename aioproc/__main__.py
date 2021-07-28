from aioproc import expose

"""example code to show how to use aioproc
"""


def echo_params(first, second=0):
    print(first)
    print(f"second={second}")


async def async_echo_params(first, second=0):
    echo_params(first, second)


expose({"echo": echo_params, "async_echo": async_echo_params})
