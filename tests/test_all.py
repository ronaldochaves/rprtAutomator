# Standard imports
import os

dir_test = os.path.dirname(__file__)

for f in sorted(os.listdir(dir_test)):
    print(f)
    if f != os.path.basename(__file__) and os.path.isfile(f) and not f.startswith('.'):
        exec(open(os.path.join(dir_test, f)).read())

print('Finished', __file__)
