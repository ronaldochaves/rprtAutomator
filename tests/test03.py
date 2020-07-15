# Standard imports
import os

# Local imports
from tools import createdocument

testDoc = createdocument.ReportDocument()
testDoc.finish()

print('Finished', os.path.realpath(__file__))
