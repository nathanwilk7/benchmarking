from locust import User, task, between

import benchmarks.utils as u


NUM_USERS = 400000
NUM_COMPANIES = 400000
NUM_EXPERIENCES_PER_USER = 20

# TODO mlflow log these suckas
PARAMS = {
    'num_users': NUM_USERS,
    'num_companies': NUM_COMPANIES,
    'num_experiences_per_user': NUM_EXPERIENCES_PER_USER,
}

USERS_TABLE_NAME = 'Users'
COMPANIES_TABLE_NAME = 'Companies'
EXPERIENCES_TABLE_NAME = 'Experiences'

USERS_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {users_table_name} (
  id SERIAL PRIMARY KEY,
  name VARCHAR
)
'''.format(users_table_name=USERS_TABLE_NAME)
COMPANIES_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {companies_table_name} (
  id SERIAL PRIMARY KEY,
  name VARCHAR
)
'''.format(companies_table_name=COMPANIES_TABLE_NAME)
EXPERIENCES_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {experiences_table_name} (
  user_id INTEGER REFERENCES {users_table_name} (id),
  company_id INTEGER REFERENCES {companies_table_name} (id)
)
'''.format(experiences_table_name=EXPERIENCES_TABLE_NAME, users_table_name=USERS_TABLE_NAME, companies_table_name=COMPANIES_TABLE_NAME)

SQL_DROP = ';'.join([f'DROP TABLE IF EXISTS {n}' for n in [EXPERIENCES_TABLE_NAME, USERS_TABLE_NAME, COMPANIES_TABLE_NAME]])
SQL_CREATE = ';'.join([USERS_TABLE_CREATE, COMPANIES_TABLE_CREATE, EXPERIENCES_TABLE_CREATE])
# TODO should this be 1 or 2 col index?
SQL_INDEX = f'CREATE INDEX ON {EXPERIENCES_TABLE_NAME} (user_id, company_id)'
SQL_INITIAL_DATA = ';'.join([
    f'INSERT INTO {USERS_TABLE_NAME} (name) SELECT n FROM generate_series(1, {NUM_USERS}) AS id, md5(random()::text) AS n',
    f'INSERT INTO {COMPANIES_TABLE_NAME} (name) SELECT n FROM generate_series(1, {NUM_COMPANIES}) AS id, md5(random()::text) AS n',
    # FODO why select distinct?
] + [f'INSERT INTO {EXPERIENCES_TABLE_NAME} SELECT DISTINCT id1, id2 FROM (SELECT generate_series(1, {NUM_USERS}) id1, ceiling(random() * {NUM_COMPANIES}) id2) q'] * NUM_EXPERIENCES_PER_USER)
SQL_SETUP = f'{SQL_DROP}; {SQL_CREATE}; {SQL_INDEX}; {SQL_INITIAL_DATA};'

def get_sql_read_user_experiences(user_id):
    return f'SELECT u.id, u.name, c.id, c.name FROM {USERS_TABLE_NAME} u JOIN {EXPERIENCES_TABLE_NAME} e ON e.user_id = u.id JOIN {COMPANIES_TABLE_NAME} c ON c.id = e.company_id WHERE u.id = {user_id}'


class LinkedIn(User):
    abstract = True
    wait_time = between(1.0, 2.0)

    def __init__(self, environment):
        super().__init__(environment)
        self.request_event = environment.events.request
        self.user_setup()

    def environment_setup():
        pass

    def user_setup(self):
        pass

    @task
    def read_user_experiences_helper(self):
        u.do_task(self, 'read_user_experiences', self.read_user_experiences)

    def read_user_experiences(self):
        raise NotImplementedError()
    
    def user_teardown(self):
        pass

    def environment_teardown():
        pass
