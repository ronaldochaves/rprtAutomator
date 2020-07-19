# Standard imports
import hashlib

def check_hash(file, hash_list, verbose=False):
    """
    Check hash of a file and compare with hashes from a list (POSIX and Windows). Verbose enables printing hash during
    tests.
    """
    fd = open(file, 'rb')  # Read in binary mode to avoid importing npTDMS library
    sha1 = hashlib.sha1(fd.read())
    file_hash = sha1.hexdigest()
    if verbose is True:
        print(file_hash)

    # Check integrity
    assert file_hash in hash_list
