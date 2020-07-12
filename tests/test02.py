# Standard imports
import hashlib
import os

# Local imports
import genTestFile


def check_hash(file, std_hash):
    fd = open(file, 'rb')  # Read in binary mode to avoid importing npTDMS library
    sha1 = hashlib.sha1(fd.read())
    file_hash = sha1.hexdigest()

    # Check integrity
    assert file_hash == std_hash


# Specify input and output folders
data_dir_input = '/Volumes/RONCHA_HD/APR-E/Fuel Pump Test Campaign/Test/input_data'
data_dir_output = '/Volumes/RONCHA_HD/APR-E/Fuel Pump Test Campaign/Test/output_data'

# Check input
file2_name = 'Turbine_Rack01_2018_11_07_15_23_58.tdms'
file2 = os.path.join(data_dir_input, file2_name)
std_hash_input = '9264aa3ff8084135fc38d7c6ad861ddf1e06b948'
check_hash(file2, std_hash_input)

# Execute function under test
genTestFile.main(data_dir_input, data_dir_output)

# Check output
file_name_output = 'DSapp_Test.csv'
file_output = os.path.join(data_dir_output, file_name_output)
std_hash_output = '9e9259ea2fa145adf07fad61c3b12df63f2a3b5a'
check_hash(file_output, std_hash_output)
