import random
import subprocess

import benchmarks.key_existence as k


class EchoGrep(k.KeyExistence):
    def environment_setup():
        with open('echogrep.txt', 'w') as w:
            for i in range(10):
                w.write(f'{i}\n')

    def insert(self):
        subprocess.run(f"echo '{random.randint(1, 10)}' >> echogrep.txt", shell=True, check=True, stdout=subprocess.DEVNULL)

    def select(self):
        temp_id = random.randint(1, 10)
        subprocess.run(f"grep {temp_id} echogrep.txt | sed -e 's/^{temp_id},//' | tail -n 1", shell=True, check=True, stdout=subprocess.DEVNULL)
