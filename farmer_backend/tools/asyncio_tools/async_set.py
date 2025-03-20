
def async_to_sync(function, *args, **kwargs):
    from asyncio import get_event_loop, new_event_loop, set_event_loop
    try:
        return get_event_loop().run_until_complete(function(*args, **kwargs))
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = new_event_loop()
            set_event_loop(loop)
            return loop.run_until_complete(function(*args, **kwargs))
        raise e