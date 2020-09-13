# Standard imports
import sys

from tools import prepare

# print(sys.argc)
print(sys.argv[0])
print(sys.argv[1])

if sys.argv[1] == 'prepare':
    prepare.main(sys.argv[2])
else:
    pass