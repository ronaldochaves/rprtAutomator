# Standard imports
import os
import sys
import time as tm

# Append project folder level to system path
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# print(sys.path)
# sys.path.append(project_dir)
# print(sys.path)

# Set tests folder
dir_tests = os.path.join(project_dir, 'tests')

# Pick test suite
test_suite = []
for entry in sorted(os.scandir(dir_tests), key=lambda ent: ent.name):
    if entry.is_file() and entry.name != os.path.basename(__file__) and not entry.name.startswith('.'):
        test_suite.append(entry)

# Run test suite
print('')
print('___***___')
print("Started test suite:", os.path.basename(__file__))
print('___***___')
start_time = tm.time()

for test in test_suite:
    print('')
    print('Running:', test.name)
    exec(open(test.path).read())

print('')
print('___***___')
print('Finished test suite:', os.path.basename(__file__), '[%.3f seconds]' % (tm.time() - start_time))
print('___***___')
