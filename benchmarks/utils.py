import time


def request_event_fire(request_event, request_type, name, start_time, end_time, exception):
    request_meta = {
        "request_type": request_type,
        "name": name,
        "response_length": 0,
        "response": None,
        "context": {},
        "exception": exception, # NOTE mark exceptions? Other things?
        "response_time": (end_time - start_time) * 1000,
    }
    request_event.fire(**request_meta)


def do_task(user, name, f, validator=None, args=[], kwargs={}):
    # import pdb; pdb.set_trace()
    if validator is None:
        validator = lambda u, r: True
    start_time = time.perf_counter()
    res, exception = None, None
    try:
        res = f(*args, **kwargs)
    except Exception as e:
        exception = e
    end_time = time.perf_counter()
    request_type = f'{user.benchmark_module}_{user.implementation_module}_{user.implementation_class}'
    if exception is None:
        exception = validator(user, res)
    request_event_fire(user.request_event, request_type, name, start_time, end_time, exception)
    return res
