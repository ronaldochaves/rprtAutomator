# Standard imports
import os
import sys
import subprocess

dir_test = os.path.dirname(os.path.realpath(__file__))

for f in sorted(os.listdir(dir_test)):
    print(f)
    if f != os.path.basename(os.path.realpath(__file__)) and os.path.isfile(f) and not f.startswith('.'):
        proc = subprocess.Popen([sys.executable, f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        (stdout, stderr) = proc.communicate()
        print(stdout.decode('utf-8'))
        if proc.returncode != 0:
            print(stderr.decode('utf-8'))
            raise Exception('ExecutionError', f)

print('Finished', os.path.realpath(__file__))
