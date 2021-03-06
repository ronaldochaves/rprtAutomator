# Standard imports
import os

# Local imports
from tools import genTestFile, check_hash

# Specify input and output folders
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_inputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')

# Check input
file_names = ['example_matfile.mat', 'example_01.tdms', 'example_02.tdms', 'example_03.tdms']
files = [os.path.join(data_dir_input, f) for f in file_names]

std_hash_inputs = [['8c7dc7c2085da896e5ca1a9297c23a25525d3e4d'], ['f7533d65629cb58c22897cb8b4490e7ed98c560d'],
                   ['2430171163f7ee53224b8bb427599c2cdac542df'], ['20867a62b44205c89d0af010af869216c6771956']]

for f, hash_input in zip(files, std_hash_inputs):
    check_hash.check_hash(f, hash_input)

# Execute function under test
print('Started testing genTestfile.py')

genTestFile.main(data_dir_output, files)

print('Finished testing genTestFile.py')

# Check output
file_name_output = 'DSapp_Test.csv'
file_output = os.path.join(data_dir_output, file_name_output)
# Use one hash for linux/macOS, and other for windows:
std_hash_output = ['a155e0495bf457abe4c585df23b66a1a3e6069ba', '9cc48bfd96a75100b31ec69761bd47c3bd31a3ab']
check_hash.check_hash(file_output, std_hash_output)
