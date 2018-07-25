# Headers
import os
import os.path as osp
import numpy as np
from datetime import datetime
from getTestInfo import add_testInfo

def checkOS():
	global runPdfLatexCmd, slsh
	if os.name == 'posix':			# unix
		slsh = '/'
		runPdfLatexCmd = 'runpdflatex-lnx.sh'
	else:
		slsh = "\\"
		runPdfLatexCmd = 'runpdflatex-win.bat'

def set_batch():
	# Define batch path
	BatPath = osp.join(BatDirPath, runPdfLatexCmd)     # change currDirPath to srchPath (or keep it in mind!)
	BatHndl = open(BatPath, 'w')						# use 'with open(tf) as f:'' (no need of ~.close())
	if os.name == 'posix':
		BatHndl.write('#!/bin/bash\n\n')
		print('roncha')
	else:
		BatHndl.write(' ')    # care with \n stuffs
	BatHndl.close()

def single_rprtGen(TDMSfilepath):
	if TDMSfilepath.endswith('.tdms'):
		compTDMSfilepath = findTDMScomp(TDMSfilepath)
		TestInfo = add_testInfo(TDMSfilepath, compTDMSfilepath)   # Struct whose fields are the wildcards found in memoFill.tex

		# Path information of the MemoTec Tex file
		memoName = 'memo_' + TestInfo.yyyy_mmm_dd + '_' + TestInfo.HHMMSSFFFFFF + '.tex'
		foldPath = osp.dirname(TDMSfilepath)
		foldName = osp.basename(foldPath)
		memoTexpath = osp.join(foldPath, memoName)
		replInfo(memoTexpath, TestInfo)

		# Writing .bat file for Tex compilation
		BatPath = osp.join(BatDirPath, runPdfLatexCmd)    # change currDirPath to srchPath (or keep it in mind!)
		BatHndl = open(BatPath, 'a')
		BatHndl.write('cd .{}{}\r\n'.format(slsh, foldName))
		latexCmd = 'pdflatex -synctex=1 -interaction=nonstopmode ' +  memoName + '\n'
		for i in range(3):    # Run 3 times to get all cross-references done at .tex
			BatHndl.write(latexCmd)
		BatHndl.write('cd ..%s\r\n' %slsh)					# Care with .bat writing 
		BatHndl.close()

		print('-> TeX file for report ' + osp.basename(TDMSfilepath) + ' generated.')
		# print('-> Run ' + runPdfLatexCmd + ' for compiling it.')
	else:
		print('The file is not a .TDMS file!')
		return()

def campaign_rprtGen(srcPath):
	count_rep = 0			# Generated reports count 
	folders = [f.path for f in os.scandir(srcPath) if f.is_dir()]
	for folder in folders:									# Scanning each folder of the directory
		TDMSfiles = [f.path for f in os.scandir(folder) if (f.name.endswith(".tdms") & f.name.startswith("COMPLETO"))]
		if TDMSfiles:
			for f_name in TDMSfiles:	   						# Scanning each TDMS file in the folders
				single_rprtGen(f_name)
				count_rep += 1
			print('-> TeX files for reports of the folder ' + folder + ' generated.')
			print('****************************************************************')
			print(' ')

	if count_rep:
		print('-> Run ' + runPdfLatexCmd + ' for compiling them.')
	else:
		print('-> No reports were generated!')		# Generic error message! Can be improved for sure!!
	# import this				# spy?

def replInfo(memoTexpath, TestInfo):					# Replace informations from template accordingly
	TargHndl = open(memoTexpath, 'w+')

	with open(TexTemplate, 'r', encoding = 'iso-8859-1') as Template:			# Remove this hardcodeness
		for line in Template:
			line = line.strip()
			if ~line.startswith('%'):   # care with 5
				starstar_count = line.count('**')
				if starstar_count == 0 | starstar_count % 2 == 1:
					print('Review memoFill.tex file. Syntax error in entry!')
					return()
				else:
					aux = line.split('**')
					for name in aux[1::2]:			# take just the odd indexes
						entryName = name
						entryValue = TestInfo[name]
						# entryValue = entryValue.replace('.', ',')
						line = line.replace('**' + entryName + '**', entryValue)
					# line = line.replace(',tex', '.tex')
					# line = line.replace(',jpg', '.jpg')
					# line = line.replace(',eps', '.eps')
			TargHndl.write(line)
			TargHndl.write('\n')
	TargHndl.close()

# A test can have 2 TDMS (low and high speed acquisition, e.g)
def findTDMScomp(TDMSfilepath):									# Find the complementary TDMS by name
	# Get list of complementaty TDMS
	fileName = osp.basename(TDMSfilepath)
	foldPath = osp.dirname(TDMSfilepath)
	foldName = osp.basename(foldPath)
	if fileName.startswith('COMPLETO'):
		TDMSfiles = [f.path for f in os.scandir(foldPath) if (f.name.endswith(".tdms") & ~f.name.startswith("COMPLETO"))]
	else:
		TDMSfiles = [f.path for f in os.scandir(foldPath) if (f.name.endswith(".tdms") & f.name.startswith("COMPLETO"))]

	# Get date & time information from TDMS file name
	time_stamp = findtimestamp(fileName)

	# Comparison by time and date (<2s delay between tdms criation, usually)
	TDMScomp = [f for f in TDMSfiles if (time_stamp - findtimestamp(f)).total_seconds() < 2]
	return TDMScomp[0]

def findtimestamp(TDMSfilename):				# Standard .tdms name: '..._HH_MM_SS_XM_DD_MM_YY_PXX.tdms'
	name_split = TDMSfilename.rsplit('_', 1)
	if name_split[0].count('_') > 6:			# Expected at least 1 '_' between '...' and 'HH_MM_SS_XM_DD_MM_YY'
		name_split = name_split[0].split('_', name_split[0].count('_') - 6)			# 6 _'s in 'HH_MM_SS_XM_DD_MM_YY'
		time_stamp_str = name_split[-1]
		time_stamp = datetime.strptime(time_stamp_str, '%I_%M_%S_%p_%d_%m_%y')
		return time_stamp
	else:
		print('You must be doing something wrong!')

# Define main method that calls other functions
def rprtGen(srchPath):
	# Look for report .tex template
	global TexTemplate, BatDirPath
	TexTemplateName = 'memoFill.tex'
	TexTemplate = osp.join(srchPath, TexTemplateName)
	isFoundTex = osp.exists(TexTemplate)

	if isFoundTex:
		checkOS()
		if osp.isfile(srchPath):
			BatDirPath = osp.basename(srchPath)
			set_batch()
			single_rprtGen(srchPath)
		elif osp.isdir(srchPath):
			BatDirPath = srchPath
			set_batch()
			campaign_rprtGen(srchPath)
		else:
			print("Invalid input!")
	else:
		print('Report template ' + TexTemplateName + ' not found in' + srchPath + '!')

# Execute main() function
if __name__ == '__main__':
	currDirPath = os.getcwd()
	print("You are here: {}!!".format(currDirPath))

	# Path to specific test data ou campaign data - user input
	srchPath = str(input('Enter file path or directory for report generation: '))
	rprtGen(srchPath)
