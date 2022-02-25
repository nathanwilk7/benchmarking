import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import random
import subprocess
import time

import psycopg2

import benchmarks.ddia_ch1_twitter_timeline as tt


# TODO move into utils?
def run_pg_query(q):
    host = 'localhost'
    port = 5433
    user = 'postgres'
    password = 'mysecretpassword'
    conn = psycopg2.connect(f'host={host} port={port} user={user} password={password}')
    cur = conn.cursor()
    cur.execute(q)
    cur.close()
    return conn.commit()


class Postgres(tt.TwitterTimeline):
    def environment_setup():
        docker_cmd = 'docker run -p 5433:5432 --rm --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres'.split()
        subprocess.Popen(docker_cmd)
        time.sleep(10)
        run_pg_query(tt.SQL_SETUP)

    def create_tweet(self):
        run_pg_query(tt.get_sql_create_tweet())

    def load_timeline(self):
        run_pg_query(tt.get_sql_load_timeline(random.randint(1, tt.NUM_USERS)))

    def environment_teardown():
        import pdb; pdb.set_trace()
        docker_cmd = 'docker kill some-postgres || true'
        subprocess.run(docker_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
