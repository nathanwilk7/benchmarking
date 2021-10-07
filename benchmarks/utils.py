import time


def request_event_fire(request_event, request_type, name, start_time, end_time):
    request_meta = {
        "request_type": request_type,
        "name": name,
        "response_length": 1,
        "response": 2,
        "context": {},
        "exception": None,
        "response_time": (end_time - start_time) * 1000,
    }
    request_event.fire(**request_meta)


def do_task(user, name, f):
	start_time = time.perf_counter()
	res = f()
	end_time = time.perf_counter()
	request_type = f'{user.benchmark_name}_{user.implementation_name}'
	request_event_fire(user.request_event, request_type, name, start_time, end_time)
	return res
