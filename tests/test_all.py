# Standard imports
import os
import sys

# Append project folder level to system path
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_dir)

# Set tests folder
dir_tests = os.path.join(project_dir, 'tests')

# Pick test suite
test_suite = []
for entry in sorted(os.scandir(dir_tests), key=lambda ent: ent.name):
    if entry.is_file() and entry.name != os.path.basename(__file__) and not entry.name.startswith('.'):
        test_suite.append(entry)

# Run test cases
print("Starting test suite", os.path.realpath(__file__))

for test in test_suite:
    print('')
    print('Running:', test.name)
    exec(open(os.path.realpath(test.path)).read())

print('')
print('Finished test suite', os.path.realpath(__file__))
print('')
