import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import random
import subprocess
import time

import psycopg2

import benchmarks.linkedin as l


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


class Postgres(l.LinkedIn):
    def environment_setup():
        docker_cmd = 'docker run -p 5433:5432 --rm --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres'.split()
        subprocess.Popen(docker_cmd)
        time.sleep(20)
        print('start running sql setup')
        run_pg_query(l.SQL_SETUP)
        print('done running sql setup')

    def read_user_experiences(self):
        run_pg_query(l.get_sql_read_user_experiences(random.randint(1, l.NUM_USERS)))

    def environment_teardown():
        docker_cmd = 'docker kill some-postgres || true'
        subprocess.run(docker_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
