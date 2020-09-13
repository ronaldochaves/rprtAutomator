# Headers
import os
import os.path as osp
from datetime import datetime, timedelta
from shutil import copy


def organize_CAMP(folder_path):
    """Given a test campaign directory with data from different DAQs, arrange all files
    into a standardized structure, categorizing in testday subdirs and run subsubdirs.
    Also, runs without all files will be arranged in a prep-testday (miscelaneous like)
    subdirs."""

    print("You are organizing this folder: {}!!".format(folder_path))
    CAMP_files = [f.path for f in os.scandir(folder_path) if f.is_file()]

    # Find  RUNS
    RUNS = find_RUNS(CAMP_files)

    # melhorar depois aqui
    prep_TD_runs = [run for run in RUNS if not isfullRUN(run)]
    prep_TD = find_TDS(prep_TD_runs)
    print(prep_TD)
    TD_runs = [run for run in RUNS if isfullRUN(run)]
    TD = find_TDS(TD_runs)
    print(TD)

    # Create new File Structure to organize campaign data files
    CAMP_folder = osp.dirname(folder_path)
    RUN_abs_count = create_FLDR_STRT(CAMP_folder, prep_TD, 'PrepTestdays')
    create_FLDR_STRT(CAMP_folder, TD, 'Testdays', RUN_abs_count)

    #    runs_dates = list(set().union(rack01_runs_dates, rack02_runs_dates, rack02_HF_runs_dates, hbm_runs_dates, MBBM_LF_runs_dates, MBBM_HF_runs_dates))

    #    # Extract information from MBBM folder name
    #    l = [find_INFO_MBBM_dirname(folder.name) for folder in MBBM_dir_runs]
    #    test_day, rel_run_test_day, abs_run, rot_nom, fluid = zip (*l)
    #    test_day = list(test_day)
    #    rel_run_test_day = list(rel_run_test_day)
    #    abs_run = list(abs_run)
    #    fluid = list(fluid)
    #    rot_nom = list(rot_nom)

    print('The campaign has {} runs distributed over {} preparation test days and {} test days!'.format(len(RUNS),
                                                                                                        len(prep_TD),
                                                                                                        len(TD)))


def find_RUNS(CAMP_files):
    """Identify all runs (and its files), even preparation ones, based on the time stamp of the files.
    The input is a list with all files of the campaign, that can be unsorted by time stamp."""

    # Sort list based on file time stamp information
    CAMP_files.sort(key=lambda file: find_TS_filename(file))

    # Identify runs and their related files
    RUNS = [[]]
    i = 0
    ind_RUN = 0
    RUN_frst_file = CAMP_files[i]
    while i < len(CAMP_files):
        if not issameRUN(RUN_frst_file, CAMP_files[i]):
            ind_RUN += 1
            RUN_frst_file = CAMP_files[i]
            RUNS.append([])
        RUNS[ind_RUN].append(CAMP_files[i])
        i += 1

    new_RUNS = [[] for run in RUNS]
    for ind_RUN, RUN in enumerate(RUNS):
        new_RUNS[ind_RUN] = split_RUN_DAQ(RUN)

    RUNS = new_RUNS

    return RUNS


def split_RUN_DAQ(RUN_file_list):
    """Split RUN (single file list) into RUN (file list for each DAQ)."""

    RUN = [[], [], [], [], [], []]
    for f in RUN_file_list:
        name = osp.basename(f)
        if (name.startswith("Turbine_IAE_Rack01_") and name.endswith(".tdms")):
            RUN[0].append(f)
        elif (name.startswith("Turbine_IAE_Rack02_") and name.endswith(".tdms")):
            RUN[1].append(f)
        elif (name.startswith("R02S06_") and name.endswith(".tdms")):
            RUN[2].append(f)
        elif (name.startswith("AGGOTurbine_") and name.endswith(".MAT")):
            RUN[3].append(f)
        elif (name.startswith("UBATUBA_AGG")):
            if name.endswith('.txt'):
                RUN[4].append(f)
            elif name.endswith('.mat'):
                RUN[5].append(f)

    return RUN


def find_TDS(RUNS_list):
    """Identify all testdays from a list of runs."""

    #    # Sort list based on file time stamp information
    #    RUNS_list.sort(key = lambda file: find_TS_filename(file[0][0][0]).date())

    # Identify runs and its related files
    TDS = [[]]
    i = 0
    ind_TD = 0
    TD_frst_run = RUNS_list[i]
    print(TD_frst_run)
    while i < len(RUNS_list):
        if not issameTD(TD_frst_run, RUNS_list[i]):
            print('roncha')
            ind_TD += 1
            TD_frst_run = RUNS_list[i]
            TDS.append([])
        TDS[ind_TD].append(RUNS_list[i])
        i += 1

    return TDS


def issameTD(RUN_1, RUN_2):
    """Verify if 2 RUNS correspond to the same TestDay comparing date from files time stamps. It is worth
    noting that RUNS can be full or not."""

    if find_TS_RUN(RUN_1).date() == find_TS_RUN(RUN_2).date():
        return True
    else:
        return False


def issameRUN(file_1, file_2):
    """Verify if 2 files correspond to the same run comparing time stamps. It is worth
    noting that time stamp can be slightly different from different racks."""

    threshold = 60  # in seconds
    if abs((find_TS_filename(file_1) - find_TS_filename(file_2)).total_seconds()) < threshold:
        return True
    else:
        return False


def isfullRUN(RUN):
    """Identify if a RUN has all data files from all DAQs."""

    len_filelist_RUN = [len(file_lst) for file_lst in RUN]
    len_filelist_DAQ = [1, 1, 1, 1, 1, 9]

    if len_filelist_RUN == len_filelist_DAQ:
        return True
    else:
        return False


def create_FLDR_STRT(CAMP_folder, TestDays, name, RUN_abs=0):
    """Create folder structure based on TestDays (or PrepTestDays) and RUNS subfolders to
    organize the campaign data."""

    TestDays_folder = osp.join(CAMP_folder, name)
    if not osp.exists(TestDays_folder):
        os.makedirs(TestDays_folder)

    RUN_abs_count = RUN_abs
    for TD in TestDays:
        TD_folder = osp.join(TestDays_folder, find_TS_RUN(TD[0]).strftime('%d-%m-%Y'))
        if not osp.exists(TD_folder):
            os.makedirs(TD_folder)
        for RUN_rel_TD, RUN in enumerate(TD):
            RUN_abs_count += 1
            RUN_TS = find_TS_RUN(RUN)
            RUN_folder_name = 'RUN' + str(RUN_rel_TD + 1).zfill(2) + '_' + 'absRUN' + str(RUN_abs_count).zfill(
                3) + '_' + RUN_TS.strftime('%H_%M_%S')
            RUN_folder = osp.join(TD_folder, RUN_folder_name)
            if not osp.exists(RUN_folder):
                os.makedirs(RUN_folder)
    #            [[copy(file, RUN_folder) for file in file_list] for file_list in RUN]

    return RUN_abs_count


def find_TS_RUN(RUN):
    """Return the time stamp of any RUN (full RUN or not)."""
    i = 0
    while not RUN[i]:
        i += 1

    return find_TS_filename(RUN[i][0])


def find_INFO_MBBM_dirname(MBBM_dirname):
    """Find run information from MBBM dirname stardardization.
    Standard MBBM folder name: Test[dlmt][mmdd][dlmt][rel_run,3][dlmt][fluid,3][dlmt]Run[abs_run,2](rpm)"""

    # Delimiters
    dlmt = '_'
    dlmt_run = 'Run'
    dlmt_rot_i = '('
    dlmt_rot_f = ')'
    thousand_sep = '.'

    # Extract data from name by splitting the name
    pref, test_day, rel_run_test_day, fluid, suf = MBBM_dirname.split(dlmt)
    abs_run, rot_nom = suf.split(dlmt_rot_i)
    abs_run = abs_run.replace(dlmt_run, '')
    rot_nom = rot_nom.replace(dlmt_rot_f, '')

    # Converting string for suitable format
    test_day = datetime.strptime('2019' + test_day, "%Y%m%d")
    rel_run_test_day = int(rel_run_test_day)
    abs_run = int(abs_run)
    rot_nom = int(rot_nom.replace(thousand_sep, ''))

    return test_day, rel_run_test_day, abs_run, rot_nom, fluid


def find_TS_filename(path, which_daq=None):
    """Find time stamp of a file based on its name."""

    if osp.isfile(path):
        name = osp.basename(path)
    else:
        print('{} is not an existing regular file!'.format(path))
        return 0

    # Time offset of PXI and MBBM
    time_offset = timedelta(minutes=51, seconds=10)

    # Deiiters
    dlmt = '_'

    dlmt_RK01 = 'Turbine_IAE_Rack01'
    dlmt_RK02 = 'Turbine_IAE_Rack02'
    dlmt_RK02_HF = 'R02S06_PXIe-4499'
    dlmt_HBM = 'AGGOTurbine'
    dlmt_MBBM = 'UBATUBA_AGG'

    pref_RK01 = dlmt_RK01 + dlmt
    pref_RK02 = dlmt_RK02 + dlmt
    pref_RK02_HF = dlmt_RK02_HF + dlmt
    pref_HBM = dlmt_HBM + dlmt
    pref_MBBM_LF = dlmt_MBBM + dlmt
    pref_MBBM_HF = dlmt_MBBM + dlmt

    file_format_PXI = '.tdms'
    file_format_HBM = '.MAT'
    file_format_MBBM_LF = '.txt'
    file_format_MBBM_HF = '.mat'

    suf_RK01 = file_format_PXI
    suf_RK02 = file_format_PXI
    suf_RK02_HF = file_format_PXI
    suf_HBM = dlmt + '1200Hz' + file_format_HBM
    suf_MBBM_LF = dlmt + '1' + dlmt + 'LF' + file_format_MBBM_LF  # UBATUBA_AGG_190705_004_17_32_05_1_1_LF.txt
    suf_MBBM_HF = dlmt + '1' + dlmt + 'HF' + file_format_MBBM_HF

    # Extract time stamp information based on standard data file naming
    if name.startswith(pref_RK01) and name.endswith(suf_RK01) or which_daq == 'RK01':
        time_stamp = datetime.strptime(name.replace(pref_RK01, '').replace(suf_RK01, ''), '%Y_%m_%d_%H_%M_%S')
    elif name.startswith(pref_RK02) and name.endswith(suf_RK02) or which_daq == 'RK02':
        time_stamp = datetime.strptime(name.replace(pref_RK02, '').replace(suf_RK02, ''), '%Y_%m_%d_%H_%M_%S')
    elif name.startswith(pref_RK02_HF) and name.endswith(suf_RK02_HF) or which_daq == 'RK02_HF':
        time_stamp = datetime.strptime(name.replace(pref_RK02_HF, '').replace(suf_RK02_HF, ''), '%d-%m-%Y_%H-%M-%S')
    elif name.startswith(pref_HBM) and name.endswith(suf_HBM) or which_daq == 'HBM':
        time_stamp = datetime.strptime(name.replace(pref_HBM, '').replace(suf_HBM, ''), '%Y_%m_%d_%H_%M_%S')
    elif name.startswith(pref_MBBM_LF) and name.endswith(suf_MBBM_LF) or which_daq == 'MBBM_LF':
        time_stamp = name.replace(pref_MBBM_LF, '').replace(suf_MBBM_LF, '').split(dlmt)
        time_stamp = time_stamp[0] + time_stamp[2] + time_stamp[3] + time_stamp[4]
        time_stamp = datetime.strptime(time_stamp, '%y%m%d%H%M%S')
        time_stamp = time_stamp - time_offset
    elif name.startswith(pref_MBBM_HF) and name.endswith(suf_MBBM_HF) or which_daq == 'MBBM_HF':
        time_stamp = name.replace(pref_MBBM_HF, '').replace(suf_MBBM_HF, '').split(dlmt)
        time_stamp = time_stamp[0] + time_stamp[2] + time_stamp[3] + time_stamp[4]
        time_stamp = datetime.strptime(time_stamp, '%y%m%d%H%M%S')
        time_stamp = time_stamp - time_offset
    else:
        print('{} does not look like a test data from this campaign!'.format(path))
        return 0

    return time_stamp


def finds_TS_metadata(file):
    pass
    return

def find_all_files(path):
    files = []
    for f in os.scandir(path):
        if f.is_file():
            files.append(f)
        else:
            files += find_all_files(f.path)
    return files


def gem_shittens(list, gem_size):
    gems = []
    list = sorted(list, key=lambda x:x.name)
    for i in range(int(len(list)/gem_size)):
        # print(i)
        gems.append(list[i*gem_size:(i+1)*gem_size])
    return gems


def find_gem_ts(gem):
    return find_TS_filename(gem[0])


def imprimir_bonito(gems, b):
    for gem in gems:
        print('')
        print('gem:', gem, 'time stamp:', find_gem_ts(gem))
        for file in gem:
            print(file.name)


def find_gem_by_ts(time_stamp, gems):
    b = [find_gem_ts(gem) for gem in gems]
    for ts in b:
        if abs((ts - time_stamp).total_seconds()) < 10*60:
            # return abstracaozinha(gems[b.index(ts)])
            return gems[b.index(ts)]

def abstracaozinha(gem):
    quem = []
    for file in gem:
        quem.append(file.name)
    return quem


def main(path):
    print('prepare: {', path, '}')
    files = find_all_files(path)
    HF_tdms_list, LF_01_tdms_list, LF_02_tdms_list, txt_list, mat_list, MAT_list = [], [], [], [], [], []
    for file in files:
        if file.name.endswith('.tdms'):
            if file.name.startswith('R02S06'):
                HF_tdms_list.append(file)
            elif file.name.startswith('Turbine_IAE_Rack01'):
                LF_01_tdms_list.append(file)
            elif file.name.startswith('Turbine_IAE_Rack02'):
                LF_02_tdms_list.append(file)
        elif file.name.endswith('.txt'):
            txt_list.append(file)
        elif file.name.endswith('.mat'):
            mat_list.append(file)
        elif file.name.endswith('.MAT'):
            MAT_list.append(file)

    # for _ in [HF_tdms_list, LF_01_tdms_list, LF_02_tdms_list, mat_list, txt_list, MAT_list]:
    #     print(len(_))
    #     for file in _:
    #         print(file.name)

    hf_tdms_gems = gem_shittens(HF_tdms_list, 1)
    lf_01_tdms_gems = gem_shittens(LF_01_tdms_list, 1)
    lf_02_tdms_gems = gem_shittens(LF_02_tdms_list, 1)
    mat_gems = gem_shittens(mat_list, 9)
    txt_gems = gem_shittens(txt_list, 1)
    MAT_gems = gem_shittens(MAT_list, 1)

    for time_stamp in [find_gem_ts(gem) for gem in hf_tdms_gems]:
        print('RUN time stamp:', time_stamp)
        gem_01 = find_gem_by_ts(time_stamp, hf_tdms_gems)
        TestDays_folder = os.path.join(os.path.dirname(path), str(time_stamp))
        if not osp.exists(TestDays_folder):
            os.makedirs(TestDays_folder)
        for i, file in enumerate(gem_01):
            copy(file, os.path.join(TestDays_folder, 'hf_' + str(i).zfill(2) + '.tdms'))

        # print(find_gem_by_ts(time_stamp, hf_tdms_gems))
        # print(find_gem_by_ts(time_stamp, lf_02_tdms_gems))
        # print(find_gem_by_ts(time_stamp, lf_01_tdms_gems))
        # print(find_gem_by_ts(time_stamp, mat_gems))
        # print(find_gem_by_ts(time_stamp, txt_gems))
        # print(find_gem_by_ts(time_stamp, MAT_gems))
        # print('')


# Execute main() function
if __name__ == '__main__':
    srchPath = ''
    print("Folder to be organized: {}!!".format(srchPath))
    organize_CAMP(srchPath)
