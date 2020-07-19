# Standard imports
import hashlib
import os
import sys

# Local imports
from tools import extract_data


def check_hash(file, hash_list):
    fd = open(file, 'rb')  # Read in binary mode to avoid importing npTDMS library
    sha1 = hashlib.sha1(fd.read())
    file_hash = sha1.hexdigest()
    print(file_hash)

    # Check integrity
    assert file_hash in hash_list


# Append project folder level to system path
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_dir)  # GitHub Actions

# Set input and output paths
data_dir_input = os.path.join(project_dir, 'tests', 'test_inputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')

# Pick raw data files
raw_files = []
for entry in sorted(os.scandir(data_dir_input), key=lambda ent: ent.name):
    if entry.is_file() and not entry.name.startswith('.'):
        if entry.name.endswith('.mat'):
            raw_files = [entry] + raw_files
        elif entry.name.endswith('.tdms'):
            raw_files.append(entry)
print('raw_files:', [f.name for f in raw_files])

# Specify list[list[var_lst]]
vars1 = ['time_HBM_LF', 'CDP_IN', 'CDP_OUT']
vars2 = ['time_PXI1_LF', 'time_abs_PXI1_LF', 'RP101SET']
vars3 = ['time_PXI2_LF', 'time_abs_PXI2_LF', 'VE401']
vars4 = ['PT501']
lst_vars = [vars1, vars2, vars3, vars4]

# Check input file hashes
std_hash_input = [['8c7dc7c2085da896e5ca1a9297c23a25525d3e4d'], ['f7533d65629cb58c22897cb8b4490e7ed98c560d'],
                  ['2430171163f7ee53224b8bb427599c2cdac542df'], ['20867a62b44205c89d0af010af869216c6771956']]
for file, hash_input in zip(raw_files, std_hash_input):
    check_hash(file.path, hash_input)

# Execute function under test
print('Started testing extract_data.py')

extract_data.main(raw_files, lst_vars, data_dir_output)

print('Finished testing extract_data.py')

# Pick extracted data files
extracted_files = []
for entry in sorted(os.scandir(data_dir_output), key=lambda ent: ent.name):
    if entry.is_file() and not entry.name.startswith('.'):
        if 'matfile' in entry.name:
            extracted_files = [entry] + extracted_files
        elif '_0' in entry.name:
            extracted_files.append(entry)
print('extracted_files:', [f.name for f in extracted_files])

# Check output file hashes
# Use one hash for linux/macOS, and other for windows:
std_hash_output = [['4b912c07682fd0cfbea4020c9ad613d54c09ac39'], ['46bf359619190bd0e41e9c2ca4f45ae8763d7c0a'],
                   ['cf2943957b5dc6c718a439ccae0c56f8d08587a8'], ['98544f9ab447f41eabe24a39c92df3fb2cc1fab4']]
for file, hash_output in zip(extracted_files, std_hash_output):
    check_hash(file.path, hash_output)
