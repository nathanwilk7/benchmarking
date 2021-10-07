import importlib
import sys

import gevent
from locust.env import Environment
from locust.log import setup_logging
import mlflow # TODO abstract out mlflow



setup_logging("INFO", None)
# TODO CLI pass in benchmark name and benchmark name? And automatically get benchmark_name/implementation_name
implementation = getattr(importlib.import_module('benchmarks.key_existence.implementations.echogrep'), 'EchoGrep')
env = Environment(user_classes=[implementation])
env.create_local_runner()
env.create_web_ui("127.0.0.1", 8089) # TODO CLI pass in port
user_count = 20 # TODO CLI?
spawn_rate_per_s = 2 # TODO CLI?
env.runner.start(user_count, spawn_rate=spawn_rate_per_s)
duration_s = 10 # TODO CLI?
gevent.spawn_later(duration_s, lambda: env.runner.quit())
env.runner.greenlet.join()


with mlflow.start_run():
    # TODO require no uncommitted?
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

env.web_ui.stop()


# TODO run seperate leader/follower processes using locust on cloud hardware/k8
