from locust import User, task, between

import benchmarks.utils as u


MIN_KEY = 0
MAX_KEY = 1000000
MAX_INITIAL_DATA_KEY = 800000
TABLE_NAME = 'KeyExistence'
COLUMN_NAME = 'key'
SQL_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({COLUMN_NAME} INTEGER)'
SQL_DROP = f'DROP TABLE IF EXISTS {TABLE_NAME}'
SQL_INITIAL_DATA = f'INSERT INTO {TABLE_NAME} SELECT g.key FROM generate_series(0, {MAX_INITIAL_DATA_KEY}) AS g (key)'
SQL_SETUP = f'{SQL_DROP}; {SQL_CREATE}; {SQL_INITIAL_DATA}'

SQL_INSERT = f'INSERT INTO {TABLE_NAME} ({COLUMN_NAME}) VALUES ({{key}})'
SQL_SELECT = f'SELECT * FROM {TABLE_NAME} WHERE {COLUMN_NAME} = {{key}}'


class KeyExistence(User):
    abstract = True
    wait_time = between(0.1, 0.2)
    min_key = 0
    max_key = 1000000

    def __init__(self, environment):
        super().__init__(environment)
        self.request_event = environment.events.request
        self.user_setup()

    def environment_setup():
        pass

    def user_setup(self):
        pass

    @task
    def insert_helper(self):
        u.do_task(self, 'insert', self.insert)

    def insert(self):
        raise NotImplementedError()

    @task
    def select_helper(self):
        u.do_task(self, 'select', self.select)

    def select(self):
        raise NotImplementedError()

    def user_teardown(self):
        pass

    def environment_teardown():
        pass
