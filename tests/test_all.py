# Standard imports
import os

dir_test = os.path.dirname(__file__)

for f in sorted(os.listdir(dir_test)):
    if f != os.path.basename(__file__):
        exec(open(os.path.join(dir_test, f)).read())

print('Finished', __file__)
