import random
import subprocess

import benchmarks.key_existence as k


# TODO immutable or use tracking?
class EchoGrep(k.KeyExistence):
	implementation_name = 'EchoGrep' # TODO use filename instead?

	def insert(self):
		subprocess.run(f"echo '{random.randint(1, 100000)}' >> echogrep.txt", shell=True, check=True, stdout=subprocess.DEVNULL)

	def select(self):
		temp_id = random.randint(1, 100000)
		subprocess.run(f"grep {temp_id} echogrep.txt | sed -e 's/^{temp_id},//' | tail -n 1", shell=True, check=True, stdout=subprocess.DEVNULL)
