# Standard imports
import os
import importlib

print("Starting all tests with", os.path.realpath(__file__))

dir_test = os.path.dirname(os.path.realpath(__file__))

for f in sorted(os.listdir(dir_test)):
    print(f)
    if f != os.path.basename(os.path.realpath(__file__)) and os.path.isfile(f) and not f.startswith('.'):
        exec(open(f).read())

print('Finished', os.path.realpath(__file__))
