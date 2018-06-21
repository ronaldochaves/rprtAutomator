# Headers
import os
import os.path as osp
import numpy as np
from datetime import datetime

# Look for report .tex template
currDirPath = os.getcwd()
TexTemplateName = 'memoFill.tex'
TexTemplate = osp.join(currDirPath, TexTemplateName)
isFoundTex = osp.exists(TexFileTemplate)
BatPath = osp.join(currDirPath, runPdfLatexCmd)    # change currDirPath to srchPath (or keep it in mind!)

def checkOS():
	global runPdfLatexCmd, slsh
	if os.name() == 'posix':			# unix
	    slsh = '/'
	    runPdfLatexCmd = 'runpdflatex-lnx.sh'
	else:
	    slsh = "\\"
	    runPdfLatexCmd = 'runpdflatex-win.bat'

def set_batch():
	# Define batch path
    BatHndl = open(BatPath, 'w')					# use 'with open(tf) as f:'' (no need of ~.close())
    if os.name() == 'posix':
        BatHndl.write('#!/bin/bash\n\n')
    else:
        BatHndl.write(' ')    # care with \n stuffs
    BatHndl.close()

def single_rprtGen(TDMSfilepath):
	if TDMSfilepath.endswith('.tdms'):
		compTDMSfilepath = findTDMScomp(TDMSfilepath)
		TestInfo = getTestInfo(TDMSfilepath, compTDMSfilepath)   # Struct whose fields are the wildcards found in memoFill.tex
		
		# Path information of the MemoTec Tex file
		memoName = 'memo_' + TestInfo.yyyy_mmm_dd + '_' + TestInfo.HHMMSSFFF + '.tex'
		foldPath = osp.dirname(TDMSfilepath)
		foldName = osp.basename(foldPath)
		memoTexpath = osp.join(foldPath, memoName)
	    replInfo(memoTexpath)
		    
	    # Writing .bat file for Tex compilation
	    BatHndl = open(BatPath, 'a')
	    BatHndl.write('cd .{}{}\r\n'.format(slsh, foldName))
	    latexCmd = 'pdflatex -synctex=1 -interaction=nonstopmode ' +  memoName + '\n'
	    for i in range(2):    # Run 3 times to get all cross-references done at .tex
	        BatHndl.write(latexCmd)
	    BatHndl.write('cd ..%s\r\n', slsh)
	    BatHndl.close()

	    print('-> TeX file for report ' + osp.basename(TDMSfilepath) + 'generated.')
	    print('-> Run ' + runPdfLatexCmd + ' for compiling it.')
	else:
		print('The file is not a TDMS file!')
		return()

def campaign_rprtGen(srcPath):
	folders = [f.path for f in os.scandir(srcPath) if f.is_dir()]
    for folder in folders:									# Scanning each folder of the directory
    	TDMSfiles = [f.path for f in os.scandir(folder) if (f.name.endswith(".tdms") & f.name.startswith("COMPLETO"))]
    	for f_name in TDMSfiles:	   						# Scanning each TDMS file in the folders
    		single_rprtGen(f_name)
    	print('-> TeX files for reports of the folder ' + folder.name + 'generated.')
    	print('****************************************************************')
    	print(' ')
    print('-> Run ' + runPdfLatexCmd + ' for compiling them.')
	print('-> Davai babuska!')			# spy

def replInfo(memoTexpath):					# Replace informations from template accordingly
	TargHndl = open(memoTexpath, 'w+')
	fild = pass

	with open(TexTemplate, 'r') as Template:
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
	                	entryValue = str(pass)
	                	# entryValue = entryValue.replace('.', ',')
	                	line = line.replace('**' + entryName + '**', entryValue)
		            # line = line.replace(',tex', '.tex')
		            # line = line.replace(',jpg', '.jpg')
		            # line = line.replace(',eps', '.eps')
		    TargHndl.write(line)
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
	TDMScomp = [f for f in TDMSfiles if (time_stamp - findtimestamp(f.name)).total_seconds() < 2]
	return TDMScomp[0]

def findtimestamp(TDMSfilename):				# Standard .tdms name: '..._HH_MM_SS_XM_DD_MM_YY_PXX.tdms'
	name_split = fileName.rsplit('_', 1)
	if name_split[0].count('_') > 6:			# Expected at least 1 '_' between '...' and 'HH_MM_SS_XM_DD_MM_YY'
		name_split = name_split[0].split('_', name_split[0].count('_') - 6)			# 6 _'s in 'HH_MM_SS_XM_DD_MM_YY'
		time_stamp_str = name_split[-1]
		time_stamp = datetime.strptime(time_stamp_str, '%I_%M_%S_%p_%d_%m_%y')
		return time_stamp
	else:
		print('You must be doing something wrong!')

# Define main method that calls other functions
def rprtGen(var):
	if isFoundTex:
		checkOS()
		set_batch()
		if osp.isfile(var):
			single_rprtGen(var)
		elif osp.isdir(var):
			campaign_rprtGen(var)
		else:
			print("Invalid input!")
	else:
		print('Report template ' + TexTemplateName + ' not found in' + currDirPath + '!')

# Execute main() function
if __name__ == '__main__':
    # Path to specific test data ou campaign data - user input
	var = str(input('Enter file path or directory for report generation: '))
	rprtGen(var)
