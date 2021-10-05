import psycogreen.gevent

psycogreen.gevent.patch_psycopg()

import os
import random
import subprocess
import sys
import time

from locust import User, task, between
import mlflow

import psycopg2

import sqlite3

import redis


# TODO pluggable use cases/scenarios/function sets/test/benchmarks and then pluggable implementations for them, all in separate files with only generic code in the base file. I think they should each have a setup func. Each use case should be a dir/module with a subdir for putting implementations. (maybe just use a uuid or dict arg so I don't live to regret the dir structure).
# and then the meat of the thing to do, the checking for correct responses should be in the test code


def run_pg_query(q):
    # TODO test performance with connection pooling?
    host = 'localhost'
    port = 5433
    user = 'postgres'
    password = 'mysecretpassword'
    conn = psycopg2.connect(f'host={host} port={port} user={user} password={password}')
    cur = conn.cursor()
    cur.execute(q)
    cur.close()
    return conn.commit()


def run_sqlite_query(q):
    file_path = 'insertselect.db'
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()


def run_redis_set(*args):
    r = redis.Redis(host='localhost', port=6380, db=0)
    r.set(*args)


def run_redis_get(k):
    r = redis.Redis(host='localhost', port=6380, db=0)
    r.get(k)


WAIT_TIME = between(0.1, 0.2)
SQL_DROP = 'DROP TABLE IF EXISTS InsertSelect;'
SQL_CREATE = 'CREATE TABLE IF NOT EXISTS InsertSelect (id INTEGER);'
SQL_SETUP = f'{SQL_DROP}; {SQL_CREATE}'


if os.getenv('LOCUST_INSERT_SELECT_POSTGRES') == 'SETUP':
    run_pg_query(SQL_SETUP)

if os.getenv('LOCUST_INSERT_SELECT_ECHOGREP') == 'SETUP':
    subprocess.run(f"rm echogrep.txt || true", shell=True, check=True, stdout=subprocess.DEVNULL)
    
if os.getenv('LOCUST_INSERT_SELECT_SQLITE') == 'SETUP':
    run_sqlite_query(SQL_DROP)
    run_sqlite_query(SQL_CREATE)

# TODO how to setup redis? run redis-cli delete all from shell? or other? restart docker from shell?


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


def do_task(user, f):
    start_time = time.perf_counter()
    name = f()
    end_time = time.perf_counter()
    request_event_fire(user.request_event, user.request_type, name, start_time, end_time)


SQL_INSERT = 'INSERT INTO InsertSelect (id) VALUES ({i});'
SQL_SELECT = 'SELECT * FROM InsertSelect WHERE id = {i};'


# TODO mark when exceptions happen or when the incorrect result is returned
# TODO connection pooling/other obvious best practices

class EchoGrepClient(User):
    request_type = 'echogrep'
    wait_time = WAIT_TIME

    def __init__(self, environment):
        super().__init__(environment)
        self.request_event = environment.events.request

    @task
    def insert(self):
        def f():
            subprocess.run(f"echo '{random.randint(1, 100000)}' >> echogrep.txt", shell=True, check=True, stdout=subprocess.DEVNULL)
            return 'insert'
        do_task(self, f)

    @task
    def select(self):
        def f():
            temp_id = random.randint(1, 100000)
            subprocess.run(f"grep {temp_id} echogrep.txt | sed -e 's/^{temp_id},//' | tail -n 1", shell=True, check=True, stdout=subprocess.DEVNULL)
            return 'select'
        do_task(self, f)


#class PostgresClient(User):
#    request_type = 'postgres'
#    wait_time = WAIT_TIME
#
#    def __init__(self, environment):
#        super().__init__(environment)
#        self.request_event = environment.events.request
#
#    @task
#    def insert(self):
#        def f():
#            run_pg_query(SQL_INSERT.format(i=random.randint(1, 100000)))
#            return 'insert'
#        do_task(self, f)
#
#    @task
#    def select(self):
#        def f():
#            run_pg_query(SQL_SELECT.format(i=random.randint(1, 100000)))
#            return 'select'
#        do_task(self, f)


#class SqliteClient(User):
#    request_type = 'sqlite'
#    wait_time = WAIT_TIME
#
#    def __init__(self, environment):
#        super().__init__(environment)
#        self.request_event = environment.events.request
#
#    @task
#    def insert(self):
#        def f():
#            run_sqlite_query(SQL_INSERT.format(i=random.randint(1, 100000)))
#            return 'insert'
#        do_task(self, f)
#
#    @task
#    def select(self):
#        def f():
#            run_sqlite_query(SQL_SELECT.format(i=random.randint(1, 100000)))
#            return 'select'
#        do_task(self, f)



#class RedisClient(User):
#    request_type = 'redis'
#    wait_time = WAIT_TIME
#
#    def __init__(self, environment):
#        super().__init__(environment)
#        self.request_event = environment.events.request
#
#    @task
#    def insert(self):
#        def f():
#            run_redis_set(random.randint(1, 100000), '')
#            return 'insert'
#        do_task(self, f)
#
#    @task
#    def select(self):
#        def f():
#            run_redis_get(random.randint(1, 100000))
#            return 'select'
#        do_task(self, f)


import gevent
from locust.env import Environment
from locust.log import setup_logging


setup_logging("INFO", None)

# setup Environment and Runner
env = Environment(user_classes=[EchoGrepClient])
env.create_local_runner()

# start a WebUI instance
env.create_web_ui("127.0.0.1", 8089)

# start a greenlet that periodically outputs the current stats
#gevent.spawn(stats_printer(env.stats))

# start a greenlet that save current stats to history
#gevent.spawn(stats_history, env.runner)

# start the test
user_count = 50
spawn_rate_per_s = 5
env.runner.start(user_count, spawn_rate=spawn_rate_per_s)

duration_s = 20
gevent.spawn_later(duration_s, lambda: env.runner.quit())

# wait for the greenlets
env.runner.greenlet.join()


# TODO run seperate leader/follower processes using locust on cloud hardware/k8
with mlflow.start_run():
    mlflow.log_param('git_repo_name', 'ddia') # basename `git rev-parse --show-toplevel`
    # TODO log benchmark and implementation
    mlflow.log_param('client', 'redis') # use case, test, query/func set, etc
    mlflow.log_param('absolute_path', '/a/b')
    mlflow.log_param('git', 'deadbe')
    mlflow.log_param('docker', 'deadbeef')
    mlflow.log_param('docker_url', 'dockerhub/blah')
    mlflow.log_param('python_version', sys.version)
    mlflow.log_param('user_count', user_count)
    mlflow.log_param('spawn_rate_per_s', spawn_rate_per_s)
    mlflow.log_param('duration_s', duration_s)
    # TODO system resources, etc, num users, frequency of query
    total_client_avg_response_time_ms = 0
    for v in env.stats.entries.values():
        with mlflow.start_run(nested=True):
            # TODO maybe also include params from parent in this run since it's not particularly queryable across parents?
            s = v.serialize()
            operation_name = s['name']
            num_requests = s['num_requests']
            total_response_time_ms = s['total_response_time']
            avg_response_time_ms = total_response_time_ms / num_requests
            total_client_avg_response_time_ms += avg_response_time_ms
            max_response_time_ms = s['max_response_time']
            min_response_time_ms = s['min_response_time']
            mlflow.log_param('operation_name', operation_name)
            mlflow.log_metric('num_requests', num_requests)
            mlflow.log_metric('total_response_time_ms', total_response_time_ms)
            mlflow.log_metric('avg_response_time_ms', avg_response_time_ms)
            mlflow.log_metric('max_response_time_ms', max_response_time_ms)
            mlflow.log_metric('min_response_time_ms', min_response_time_ms)
            # TODO percentile metrics or other useful numbers

    mlflow.log_metric('total_client_avg_response_time_ms', total_client_avg_response_time_ms)
    # TODO if files exist, log
    # TODO log stats files or other useful CSV's
    mlflow.log_artifact("requirements.txt")
    #mlflow.log_artifact("Dockerfile")

# stop the web server for good measures
env.web_ui.stop()

