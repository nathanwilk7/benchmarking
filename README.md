# setup

# pyenv
brew install pyenv
Add pyenv home/etc to path and eval pyenv --path
brew install postgresql

# pip
python -m venv venv

# venv
source venv/bin/activate

# pip
pip install -r requirements.txt

# docker

install docker...

# run
python benchmark.py

http://localhost:8089

# metrics

mlflow ui

# name ideas

anciano
The unbenchmarked design is not worth designing
benchmark the living daylights out of everything all of the time

# postgres debug
docker run -it --rm --network host --name some-psql postgres psql -U postgres -h localhost -p 5432 postgres

# old

# redis
docker run -p 6380:6379 --rm --name some-redis redis

docker run -it --network host --rm redis redis-cli -p 6380

