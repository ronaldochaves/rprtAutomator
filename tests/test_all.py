# Standard imports
import os
import subprocess

dir_test = os.path.dirname(os.path.realpath(__file__))
print('dir_test:', dir_test)
print('wtf')
print('os.listdir(dir_test)', os.listdir(dir_test))  # Debugging on GitHub
for f in sorted(os.listdir(dir_test)):
    print(f)
    if f != os.path.basename(os.path.realpath(__file__)) and os.path.isfile(f) and not f.startswith('.'):
        ret = os.system("python " + os.path.join(dir_test, f))
        print(ret)
        proc = subprocess.Popen(
            ["python", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        (stdout, stderr) = proc.communicate()
        print(stdout.decode('utf-8'))
        if proc.returncode != 0:
            print(stderr)
            raise Exception('ExecutionError', f)

print('Finished', os.path.realpath(__file__))
