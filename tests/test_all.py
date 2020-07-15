# Standard imports
import os

print("Starting the test suite", os.path.realpath(__file__))

dir_test = os.path.dirname(os.path.realpath(__file__))

for f in sorted(os.listdir(dir_test)):
    print('')
    print('Conditions for file:', f)
    print('f != os.path.basename(os.path.realpath(__file__)) -->', f != os.path.basename(os.path.realpath(__file__)))
    print('os.path.isfile(os.path.join(dir_test, f)) -->', os.path.isfile(os.path.join(dir_test, f)))
    print("not f.startswith('.') -->", not f.startswith('.'))
    if f != os.path.basename(os.path.realpath(__file__)) and os.path.isfile(os.path.join(dir_test, f)) and not f.startswith('.'):
        print('Running:', f)
        exec(open(os.path.join(dir_test, f)).read())

print('')
print('Finished the test suite', os.path.realpath(__file__))
