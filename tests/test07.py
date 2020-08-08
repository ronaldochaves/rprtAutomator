# Standard imports
import os

# Local imports
from tools import transform_data, check_hash, oop_implementation

# Set input and output paths
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir_input = os.path.join(project_dir, 'tests', 'test_outputs')
data_dir_output = os.path.join(project_dir, 'tests', 'test_outputs')

# Globals
delimiter = '_'
template_repo_path = 'XXX/templates'
TexTemplateName = 'memoFill.tex'
memoFormatName = 'memotecFormat.tex'
logoName1 = 'logo_IAE.jpg'
# logoName2 = logo2
build_dir = 'XXX/Outputs'


##############################################################################
# Initializing
# DAQ_1 = DAQ.PXI_LF_01()
# DAQ_2 = DAQ.PXI_LF_02()
# DAQ_3 = DAQ.PXI_HF()
# DAQ_4 = DAQ.HBM()
# DAQ_5 = DAQ.DAQX_LF()
# DAQ_6 = DAQ.DAQX_HF()
#
# file_1 = '/XXX/' + HBMpref + '_2020_01_24_10_30_44_1200Hz.mat'
# file_2 = '/XXX/Turbine_IAE_Rack01_2020_01_25_11_31_41.tdms'
# file_6 = '/XXX/Turbine_IAE_Rack02_2020_01_25_11_31_41.tdms'
# file_3 = '/XXX/Turbine_IAE_Rack01_2020_01_25_12_31_42.tdms'
# file_4 = '/XXX/Turbine_IAE_Rack02_2020_01_25_12_31_42.tdms'
# file_5 = '/XXX/' + daqPref2 + '_200125_001_13_22_52_1_HF.mat'
#
# Run_1 = Run(datetime(2020, 1, 24, 10, 30, 40), [file_1])
# Run_2 = Run(datetime(2020, 1, 25, 12, 31, 41), [file_2, file_6])
# Run_3 = Run(datetime(2020, 1, 25, 13, 32, 42), [file_3, file_4, file_5])
#
# TD_1 = TestDay(date(2020, 1, 24), 'deu bom!', [Run_1])
# TD_2 = TestDay(date(2020, 1, 25), 'deu bom demais!', [Run_2, Run_3])
# TD_3 = TestDay(date(2020, 1, 26), 'deu bom demais so!')
#
# DAQ_list_1 = [DAQ_1, DAQ_2, DAQ_3, DAQ_4, DAQ_5, DAQ_6]
# DAQ_list_2 = [DAQ_4, DAQ_5, DAQ_6]
#
# jeri = TestCamp('JERICOACoARA', 'Turbine', 'ITAU', 'Client1', DAQ_list_1, [TD_1, TD_2, TD_3])
# ch_verde = TestCamp('CHEIROVERDE', 'Chamber', 'BRADESCO', 'Client2', DAQ_list_2, [TD_1, TD_2, TD_3])
#
# # Printing
# print(jeri)
# print('')
# jeri.print_DAQs()
# print('')
# jeri.print_TDs()
# print('----------------------------------------------------------')
# print('----------------------------------------------------------')
# print(ch_verde)
# print('')
# ch_verde.print_DAQs()
# print('')
# ch_verde.print_TDs()
# print('----------------------------------------------------------')
# print('----------------------------------------------------------')
# jeri.TD_lst[1].print_Runs()
# jeri.TD_lst[1].Run_lst[0].print_files()
# jeri.TD_lst[1].Run_lst[1].print_files()
# print('----------------------------------------------------------')
# print('----------------------------------------------------------')
