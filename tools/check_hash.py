# Standard imports
import hashlib

def check_hash(file, hash_list, verbose=False):
    fd = open(file, 'rb')  # Read in binary mode to avoid importing npTDMS library
    sha1 = hashlib.sha1(fd.read())
    file_hash = sha1.hexdigest()
    if verbose is True:
        print(file_hash)

    # Check integrity
    assert file_hash in hash_list
