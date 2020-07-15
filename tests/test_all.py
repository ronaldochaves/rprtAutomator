# Standard imports
import os
import sys

# Append project folder level to system path
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_dir)

# Set tests folder
dir_tests = os.path.join(project_dir, 'tests')
print(__file__)

# Pick test suite
test_suite = []
for entry in sorted(os.scandir(), key=lambda ent: ent.name):
    if entry.is_file() and entry.name != os.path.basename(__file__) and not entry.name.startswith('.'):
        test_suite.append(entry)

# Run test cases
print("Starting test suite", os.path.realpath(__file__))

for test in test_suite:
    print('Running:', test.name)
    exec(open(test.path).read())

# for f in sorted(os.listdir(dir_test)):
#     print('')
#     print('Conditions for file:', f)
#     print('f != os.path.basename(os.path.realpath(__file__)) -->', f != os.path.basename(os.path.realpath(__file__)))
#     print('os.path.isfile(os.path.join(dir_test, f)) -->', os.path.isfile(os.path.join(dir_test, f)))
#     print("not f.startswith('.') -->", not f.startswith('.'))
#     if f != os.path.basename(os.path.realpath(__file__)) and os.path.isfile(os.path.join(dir_test, f)) and not f.startswith('.'):
#         print('Running:', f)
#         exec(open(os.path.join(dir_test, f)).read())

print('')
print('Finished test suite', os.path.realpath(__file__))
