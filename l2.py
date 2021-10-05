import os
import random
import subprocess
import sys
import time

from locust import User, task, between


WAIT_TIME = between(0.1, 0.2)


def request_event_fire(request_event, request_type, name, start_time, end_time):
    request_meta = {
        "request_type": request_type,
        "name": name,
        "response_length": 1,  # calculating this for an xmlrpc.client response would be too hard
        "response": 2,
        "context": {},  # see HttpUser if you actually want to implement contexts
        "exception": None,
        "response_time": (time.perf_counter() - start_time) * 1000,
    }
    request_event.fire(**request_meta)


def do_task(user, name, f):
    start_time = time.perf_counter()
    res = f()
    end_time = time.perf_counter()
    request_event_fire(user.request_event, user.request_type, name, start_time, end_time)
    return res


class BenchmarkA(User):
    abstract = True
    kwargs = {'n': 0}
    request_type = 'A'
    wait_time = WAIT_TIME

    def __init__(self, environment):
        super().__init__(environment)
        self.request_event = environment.events.request

    @task
    def a(self):
        n = self.kwargs['n']
        r = do_task(self, 'a', self.ah)
        n += 1
        self.kwargs['n'] = n
        assert r == n, (r, n)

    def ah(self):
        raise NotImplementedError()


class BenchmarkAImplementation(BenchmarkA):
    sub_kwargs = {'sn': 0}

    def ah(self):
        n = self.kwargs['n']
        sn = self.sub_kwargs['sn']
        print(n, sn)
        self.kwargs['n'] = n
        sn += 1
        self.sub_kwargs['sn'] = sn
        return sn


import gevent
from locust.env import Environment
from locust.log import setup_logging


setup_logging("INFO", None)

# setup Environment and Runner
env = Environment(user_classes=[BenchmarkAImplementation])
env.create_local_runner()

# start a WebUI instance
env.create_web_ui("127.0.0.1", 8089)

# start the test
user_count = 2
spawn_rate_per_s = 1
env.runner.start(user_count, spawn_rate=spawn_rate_per_s)

duration_s = 5
gevent.spawn_later(duration_s, lambda: env.runner.quit())

# wait for the greenlets
env.runner.greenlet.join()

# stop the web server for good measures
env.web_ui.stop()

