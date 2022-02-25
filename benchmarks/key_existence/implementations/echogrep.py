import random
import subprocess

import benchmarks.key_existence as k


class EchoGrep(k.KeyExistence):
    def environment_setup():
        with open('echogrep.txt', 'w') as w:
            for i in range(k.MIN_KEY, k.MAX_KEY):
                w.write(f'{i}\n')

    def insert(self):
        subprocess.run(f"echo '{random.randint(k.MIN_KEY, k.MAX_KEY)}' >> echogrep.txt", shell=True, check=True, stdout=subprocess.DEVNULL)

    def select(self):
        temp_id = random.randint(k.MIN_KEY, k.MAX_KEY)
        subprocess.run(f"grep {temp_id} echogrep.txt | sed -e 's/^{temp_id},//' | tail -n 1", shell=True, check=True, stdout=subprocess.DEVNULL)
