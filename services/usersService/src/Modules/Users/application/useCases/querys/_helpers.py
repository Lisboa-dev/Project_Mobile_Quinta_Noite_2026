from inspect import isawaitable


async def maybe_await(value):
    if isawaitable(value):
        return await value
    return value
