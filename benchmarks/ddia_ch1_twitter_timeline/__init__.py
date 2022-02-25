from locust import User, task, between

import benchmarks.utils as u


# https://www.linkedin.com/pulse/what-scalability-paolo-vernucci/


FOCUS_READ = 'read'
FOCUS_WRITE = 'write'
LOAD_FOCUS = FOCUS_READ

NUM_USERS = 100
NUM_FOLLOWERS_PER_USER = 10 # Approximate b/c of how I'm filtering dups

# TODO rename plural USERS
USER_TABLE_NAME = 'Users'
FOLLOWS_TABLE_NAME = 'Follows'
TWEETS_TABLE_NAME = 'Tweets'

USER_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {user_table_name} (
  id SERIAL PRIMARY KEY,
  screen_name VARCHAR
)
'''.format(user_table_name=USER_TABLE_NAME)
FOLLOWS_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {follows_table_name} (
  follower_id INTEGER REFERENCES {user_table_name} (id),
  followee_id INTEGER REFERENCES {user_table_name} (id),
  UNIQUE(follower_id, followee_id)
)
'''.format(follows_table_name=FOLLOWS_TABLE_NAME, user_table_name=USER_TABLE_NAME)
TWEETS_TABLE_CREATE = '''
CREATE TABLE IF NOT EXISTS {tweets_table_name} (
  id SERIAL PRIMARY KEY,
  sender_id INTEGER REFERENCES {user_table_name} (id),
  text VARCHAR,
  timestamp TIMESTAMP DEFAULT NOW()
)
'''.format(user_table_name=USER_TABLE_NAME, tweets_table_name=TWEETS_TABLE_NAME)

SQL_CREATE = ';'.join([USER_TABLE_CREATE, FOLLOWS_TABLE_CREATE, TWEETS_TABLE_CREATE])
SQL_DROP = ';'.join([f'DROP TABLE IF EXISTS {n}' for n in [USER_TABLE_NAME, FOLLOWS_TABLE_NAME, TWEETS_TABLE_NAME]])
SQL_INITIAL_DATA = ';'.join([
    f'INSERT INTO {USER_TABLE_NAME} (screen_name) SELECT sn FROM generate_series(1, {NUM_USERS}) AS id, md5(random()::text) AS sn',
    f'INSERT INTO {FOLLOWS_TABLE_NAME} SELECT DISTINCT id1, id2 FROM (SELECT generate_series(1, {NUM_USERS}) id1, ceiling(random() * {NUM_USERS}) id2 from generate_series(1, {NUM_FOLLOWERS_PER_USER})) s WHERE id1 <> id2',
])
SQL_SETUP = f'{SQL_DROP}; {SQL_CREATE}; {SQL_INITIAL_DATA};'


def get_sql_create_tweet():
    return f'INSERT INTO {TWEETS_TABLE_NAME} (sender_id, text) VALUES (ceiling(random() * {NUM_USERS}), md5(random()::text));'


def get_sql_load_timeline(user_id):
    return f'SELECT {TWEETS_TABLE_NAME}.id, {TWEETS_TABLE_NAME}.text, {TWEETS_TABLE_NAME}.timestamp, {USER_TABLE_NAME}.id, {USER_TABLE_NAME}.screen_name FROM {TWEETS_TABLE_NAME} JOIN {USER_TABLE_NAME} ON {TWEETS_TABLE_NAME}.sender_id = {USER_TABLE_NAME}.id JOIN {FOLLOWS_TABLE_NAME} ON {FOLLOWS_TABLE_NAME}.followee_id = {USER_TABLE_NAME}.id WHERE {FOLLOWS_TABLE_NAME}.follower_id = {user_id} ORDER BY Tweets.timestamp;'


# TODO break into a "cache" on write version
class TwitterTimeline(User):
    abstract = True
    wait_time = between(0.05, 0.10)

    def __init__(self, environment):
        super().__init__(environment)
        self.request_event = environment.events.request
        self.user_setup()

    def environment_setup():
        pass

    def user_setup(self):
        pass

    @task
    def create_tweet_helper(self):
        u.do_task(self, 'create_tweet', self.create_tweet)

    def create_tweet(self):
        raise NotImplementedError()

    @task
    def load_timeline_helper(self):
        u.do_task(self, 'load_timeline', self.load_timeline)

    def load_timeline(self):
        raise NotImplementedError()

    def user_teardown(self):
        pass

    def environment_teardown():
        pass
