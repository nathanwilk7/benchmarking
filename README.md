# pip
python -m venv venv

# venv
source venv/bin/activate

# pip
pip install -r requirements.txt

# postgres
docker run -p 5433:5432 --rm --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres

docker run -it --rm --network host --name some-psql postgres psql -U postgres -h localhost -p 5432 postgres

# redis
docker run -p 6380:6379 --rm --name some-redis redis

docker run -it --network host --rm redis redis-cli -p 6380

# setup
LOCUST_INSERT_SELECT_POSTGRES=SETUP LOCUST_INSERT_SELECT_ECHOGREP=SETUP LOCUST_INSERT_SELECT_SQLITE=SETUP LOCUST_INSERT_SELECT_REDIS=SETUP python locustfile.py

# run
locust

The unbenchmarked design is not worth designing

# name ideas

anciano
