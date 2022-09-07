import random
import subprocess
import time

from pymongo import MongoClient

import benchmarks.linkedin as l


# TODO move into utils?
def run_mongo_query(user_id):
    client = MongoClient('localhost:27017', replicaset='dbrs')
    db = client.mydb
    return db.users.find_one({'_id': user_id})

class Mongo(l.LinkedIn):
    def environment_setup():
        shell_cmd = ['./benchmarks/linkedin/implementations/mongo/startdb.sh']
        subprocess.Popen(shell_cmd)
        time.sleep(45)
        # TODO dry    
        client = MongoClient('localhost:27017', replicaset='dbrs')
        db = client.mydb
        import uuid
        u = uuid.uuid4().hex
        print('generating data')
        users = [
            {
                '_id': user_id,
                'name': u,
                'experiences': [
                    {
                        'company_id': random.randint(1, l.NUM_COMPANIES + 1),
                        'company_name': u,
                    }
                    for _ in range(1, l.NUM_EXPERIENCES_PER_USER + 1)
                ]
            }
            for user_id in range(1, l.NUM_USERS + 1)
        ]
        print('starting data insert', len(users))
        r = db.users.insert_many(users)
        print('done with data insert')

    def read_user_experiences(self):
        run_mongo_query(random.randint(1, l.NUM_USERS))

    def environment_teardown():
        shell_cmd = 'cd benchmarks/linkedin/implementations/mongo && docker compose down -v && rm -rf /Users/nathanwilkinson/mongors || true'
        subprocess.run(shell_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
