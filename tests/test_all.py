# Standard imports
import os

dir_test = os.path.dirname(os.path.realpath(__file__))
print('dir_test:', dir_test)
print('wtf')
print('os.listdir(dir_test)', os.listdir(dir_test))  # Debugging on GitHub
for f in sorted(os.listdir(dir_test)):
    print(f)
    if f != os.path.basename(__file__) and os.path.isfile(f) and not f.startswith('.'):
        exec(open(os.path.join(dir_test, f)).read())

print('Finished', __file__)
