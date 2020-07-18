# Standard imports
import os

# Local imports
from tools import createdocument

print('Started testing createdocument.py')

testDoc = createdocument.ReportDocument(file_name_prefix='report_test03_v')
testDoc.finish()
print('Finished', os.path.realpath(__file__))

print('Finished testing createdocument.py')
