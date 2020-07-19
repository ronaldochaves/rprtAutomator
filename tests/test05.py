# Standard imports
import os

# Local imports
from tools import transform_data, check_hash

# Set input and output paths
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_outputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')

# Pick extracted data files
extracted_files = []
for entry in sorted(os.scandir(data_dir_output), key=lambda ent: ent.name):
    if entry.is_file() and '_extracted' in entry.name and not entry.name.startswith('.'):
        if 'matfile' in entry.name:
            extracted_files = [entry] + extracted_files
        elif '_0' in entry.name:
            extracted_files.append(entry)
print('extracted_files:', [f.name for f in extracted_files])

# Check input file hashes
# Use one hash for linux/macOS, and other for windows:
std_hash_input = [['4b912c07682fd0cfbea4020c9ad613d54c09ac39'], ['46bf359619190bd0e41e9c2ca4f45ae8763d7c0a'],
                  ['cf2943957b5dc6c718a439ccae0c56f8d08587a8'], ['98544f9ab447f41eabe24a39c92df3fb2cc1fab4']]
for file, hash_input in zip(extracted_files, std_hash_input):
    check_hash.check_hash(file.path, hash_input)

# Specify list[list[var_lst]]
vars1 = ['time_HBM_LF', 'CDP_IN', 'CDP_OUT']
vars2 = ['time_PXI1_LF', 'time_abs_PXI1_LF', 'RP101SET']
vars3 = ['time_PXI2_LF', 'time_abs_PXI2_LF', 'VE401']
vars4 = ['PT501']
lst_vars = [vars1, vars2, vars3, vars4]

# Execute function under test
print('Started testing transform_data.py')

transform_data.main(extracted_files, data_dir_output)

print('Finished testing transform_data.py')

# Pick transformed data files
transformed_files = []
for entry in sorted(os.scandir(data_dir_output), key=lambda ent: ent.name):
    if entry.is_file() and '_transformed' in entry.name and not entry.name.startswith('.'):
        transformed_files.append(entry)
print('transformed_files:', [f.name for f in transformed_files])

# Check output file hashes
# Use one hash for linux/macOS, and other for windows:
std_hash_output = [['b386ccbbc532eb1a32a49770da33b5737e62d243']]
for file, hash_output in zip(transformed_files, std_hash_output):
    check_hash.check_hash(file.path, hash_output)
