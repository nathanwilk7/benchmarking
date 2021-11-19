# Does importing this first matter?
import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import random
import subprocess
import time

import psycopg2

import benchmarks.key_existence as k


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


class Postgres(k.KeyExistence):
    def environment_setup():
        docker_cmd = 'docker run -p 5433:5432 --rm --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres'.split()
        subprocess.Popen(docker_cmd)
        # TODO verify exit code/etc?
        time.sleep(3) # TODO real check that postgres is up
        run_pg_query(k.SQL_SETUP)

    def insert(self):
        key = random.randint(self.min_key, self.max_key) # NOTE max off by one
        run_pg_query(k.SQL_INSERT.format(key=key))

    def select(self):
        key = random.randint(self.min_key, self.max_key)
        run_pg_query(k.SQL_SELECT.format(key=key))

    def environment_teardown():
        docker_cmd = 'docker kill some-postgres || true'
        subprocess.run(docker_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)