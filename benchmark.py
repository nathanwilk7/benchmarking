import importlib
import sys

import gevent
from locust.env import Environment
from locust.log import setup_logging
import mlflow


if __name__ == '__main__':

    # CONFIG
    benchmark_name = 'ddia_ch1_twitter_timeline'
    implementation_name = 'Postgres'
    implementation_class = implementation_name
    # END CONFIG

    setup_logging("INFO", None)

    m = importlib.import_module(f'benchmarks.{benchmark_name}.implementations.{implementation_name}')
    implementation = getattr(m, implementation_class)
    implementation.benchmark_module = benchmark_name
    implementation.implementation_module = implementation_name
    implementation.implementation_class = implementation_class
    try:
        implementation.environment_setup()
        env = Environment(user_classes=[implementation])
        env.create_local_runner()
        env.create_web_ui("127.0.0.1", 8089)
        user_count = 50
        spawn_rate_per_s = 5
        env.runner.start(user_count, spawn_rate=spawn_rate_per_s)
        duration_s = 300
        gevent.spawn_later(duration_s, lambda: env.runner.quit())
        env.runner.greenlet.join()
        env.web_ui.stop()
    finally:
        implementation.environment_teardown()


    with mlflow.start_run():
        mlflow.log_param('git_repo_name', 'ddia')
        mlflow.log_param('user', 'redis')
        mlflow.log_param('absolute_path', '/a/b')
        mlflow.log_param('git', 'deadbe')
        mlflow.log_param('docker', 'deadbeef')
        mlflow.log_param('docker_url', 'dockerhub/blah')
        mlflow.log_param('python_version', sys.version)
        mlflow.log_param('user_count', user_count)
        mlflow.log_param('spawn_rate_per_s', spawn_rate_per_s)
        mlflow.log_param('duration_s', duration_s)
        total_user_avg_response_time_ms = 0
        for v in env.stats.entries.values():
            with mlflow.start_run(nested=True):
                s = v.serialize()
                operation_name = s['name']
                num_requests = s['num_requests']
                total_response_time_ms = s['total_response_time']
                avg_response_time_ms = total_response_time_ms / num_requests
                total_user_avg_response_time_ms += avg_response_time_ms
                max_response_time_ms = s['max_response_time']
                min_response_time_ms = s['min_response_time']
                mlflow.log_param('operation_name', operation_name)
                mlflow.log_metric('num_requests', num_requests)
                mlflow.log_metric('total_response_time_ms', total_response_time_ms)
                mlflow.log_metric('avg_response_time_ms', avg_response_time_ms)
                mlflow.log_metric('max_response_time_ms', max_response_time_ms)
                mlflow.log_metric('min_response_time_ms', min_response_time_ms)

        mlflow.log_metric('total_user_avg_response_time_ms', total_user_avg_response_time_ms)
        mlflow.log_artifact("requirements.txt")
