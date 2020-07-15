%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Generate a sample .mat file that can be used for running tests.
%
% Written by Rian Koja for publishing in GitHub with a specified license.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Get location where .mat will be saved:
dir_file = fileparts(mfilename('fullpath'));
dir_test_inputs = fullfile(dir_file, '..', 'tests', 'test_inputs');

% Start creating variables for .mat:
Channel_1_Data = linspace(0, 1, 1200);
Channel_26_Data = heaviside(Channel_1_Data - 0.35)... 
                - heaviside(Channel_1_Data - 0.85);
Channel_33_Data = 2*Channel_26_Data;

% Create .mat:
mat_filename = fullfile(dir_test_inputs, 'example_matfile.mat');
save(mat_filename, 'Channel_1_Data', 'Channel_26_Data', 'Channel_33_Data')

fprintf('Finished %s\n', mfilename())


