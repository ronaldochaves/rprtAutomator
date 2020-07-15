# Standard imports
import os

# Local imports
from tools import createdocument

testDoc = createdocument.ReportDocument(file_name_prefix='test03_report_v')
testDoc.finish()

print('Finished', os.path.realpath(__file__))
