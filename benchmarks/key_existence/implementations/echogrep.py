import random
import subprocess

import benchmarks.key_existence as k


class EchoGrep(k.KeyExistence):
	def environment_setup():
		with open('echogrep.txt', 'w') as w:
			for i in range(10):
				w.write(f'{i}\n')

	def insert(self, i):
		subprocess.run(f"echo '{i}' >> echogrep.txt", shell=True, check=True, stdout=subprocess.DEVNULL)
		return i

	def select(self, i):
		r = subprocess.run(f"grep {i} echogrep.txt | tail -n 1", shell=True, check=True, capture_output=True)
		if r.stdout:
			return i

		return None
