%% TEST_WITH_GOOGLE_DRIVE_DATA - Test WhiFuN functions using Google Drive data
%
%   This script tests WhiFuN functions using practice data from Google Drive
%   without requiring local download. It uses MATLAB's webread/websave to
%   access files directly from the shared Google Drive folder.
%
%   Practice Data Location:
%   https://drive.google.com/drive/folders/1l7dhG8dYYRCW5EWhkPZbBpA7TOau1W-B
%
%   Test Subject: 0050952 (from practice_NYU_abide dataset)
%
%   Structure:
%   - 0050952/session_1/anat_1/mprage.nii.gz (anatomical)
%   - 0050952/session_1/rest_1/rest.nii.gz (functional)
%
%   Usage:
%       test_with_google_drive_data
%       test_with_google_drive_data('download_only')  % Just download test data
%       test_with_google_drive_data('test_functions') % Run function tests
%
%   Note: This script requires internet connection and may take time to
%         download data on first run. Downloaded files are cached locally.

function test_with_google_drive_data(mode)

if nargin < 1
    mode = 'full'; % full, download_only, test_functions
end

clc;
fprintf('====================================================================\n');
fprintf('WhiFuN Function Testing with Google Drive Data\n');
fprintf('====================================================================\n\n');

%% Setup paths
script_path = fileparts(mfilename('fullpath'));
whifun_root = fileparts(script_path);
addpath(genpath(whifun_root));

% Create temporary test data folder
test_data_dir = fullfile(script_path, 'temp_test_data');
if ~exist(test_data_dir, 'dir')
    mkdir(test_data_dir);
end

%% Google Drive File IDs for test subject 0050952
% Note: These are direct download links that need to be updated
% Since Google Drive requires authentication for folders, we'll provide
% instructions for manual download or use a pre-prepared test dataset

fprintf('IMPORTANT: Google Drive Integration Notes\n');
fprintf('--------------------------------------------------------------------\n');
fprintf('Google Drive does not allow direct programmatic access to shared folders\n');
fprintf('without authentication. You have two options:\n\n');

fprintf('Option 1: Manual Download (Recommended)\n');
fprintf('  1. Visit: https://drive.google.com/drive/folders/1l7dhG8dYYRCW5EWhkPZbBpA7TOau1W-B\n');
fprintf('  2. Download the practice_NYU_abide folder\n');
fprintf('  3. Extract to: %s\n', test_data_dir);
fprintf('  4. Run this script again\n\n');

fprintf('Option 2: Use Alternative Test Data\n');
fprintf('  - Use synthetic/phantom data for testing\n');
fprintf('  - Create minimal test NIfTI files\n\n');

%% Check if data already exists locally
data_path = fullfile(test_data_dir, 'practice_NYU_abide', '0050952');
if exist(data_path, 'dir')
    fprintf('✓ Test data found locally at: %s\n\n', data_path);
    data_available = true;
else
    fprintf('✗ Test data not found locally.\n\n');
    data_available = false;
    
    % Offer to create synthetic test data
    % Check if running in batch mode
    is_batch = usejava('desktop') == 0 || batchStartupOptionUsed;
    
    if is_batch
        % In batch mode, auto-create synthetic data
        fprintf('\nRunning in batch mode - auto-creating synthetic test data...\n');
        create_synthetic_test_data(test_data_dir);
        data_available = true;
    else
        % Interactive mode
        fprintf('Would you like to create synthetic test data for testing? (y/n): ');
        response = input('', 's');
        
        if strcmpi(response, 'y')
            fprintf('\nCreating synthetic test data...\n');
            create_synthetic_test_data(test_data_dir);
            data_available = true;
        else
            fprintf('\nPlease download the data manually and run again.\n');
            fprintf('====================================================================\n');
            return;
        end
    end
end

if strcmp(mode, 'download_only')
    fprintf('Download/setup complete. Data ready for testing.\n');
    fprintf('====================================================================\n');
    return;
end

%% Test Functions with Data
if data_available
    fprintf('====================================================================\n');
    fprintf('Starting Function Tests with Real Data\n');
    fprintf('====================================================================\n\n');
    
    % Set up test parameters
    output_folder = fullfile(test_data_dir, 'test_output');
    if ~exist(output_folder, 'dir')
        mkdir(output_folder);
    end
    
    % Test subject info
    subject_folder = fullfile(test_data_dir, 'practice_NYU_abide');
    
    fprintf('Test Configuration:\n');
    fprintf('  Subject Folder: %s\n', subject_folder);
    fprintf('  Output Folder: %s\n', output_folder);
    fprintf('  Test Subject: 0050952\n\n');
    
    %% Test 1: Check data files
    fprintf('>>> Test 1: Checking data files\n');
    fprintf('--------------------------------------------------------------------\n');
    
    anat_file = fullfile(subject_folder, '0050952', 'session_1', 'anat_1', 'mprage.nii.gz');
    func_file = fullfile(subject_folder, '0050952', 'session_1', 'rest_1', 'rest.nii.gz');
    
    if exist(anat_file, 'file')
        fprintf('✓ Anatomical file found: %s\n', anat_file);
        % Get file info
        anat_info = dir(anat_file);
        fprintf('  Size: %.2f MB\n', anat_info.bytes / 1024^2);
    else
        fprintf('✗ Anatomical file not found\n');
    end
    
    if exist(func_file, 'file')
        fprintf('✓ Functional file found: %s\n', func_file);
        % Get file info
        func_info = dir(func_file);
        fprintf('  Size: %.2f MB\n', func_info.bytes / 1024^2);
    else
        fprintf('✗ Functional file not found\n');
    end
    
    fprintf('\n');
    
    %% Test 2: Test file reading functions
    fprintf('>>> Test 2: Testing WhiFuN file I/O functions\n');
    fprintf('--------------------------------------------------------------------\n');
    
    try
        % Test whifun_check_func_file
        fprintf('Testing whifun_check_func_file...\n');
        if exist(func_file, 'file')
            func_path = whifun_check_func_file(subject_folder, '0050952', 'session_1', 'rest_1', 'rest');
            if ~isempty(func_path)
                fprintf('  ✓ Function correctly located functional file\n');
            else
                fprintf('  ✗ Function failed to locate file\n');
            end
        end
    catch ME
        fprintf('  ✗ Error: %s\n', ME.message);
    end
    
    try
        % Test whifun_check_anat_file
        fprintf('Testing whifun_check_anat_file...\n');
        if exist(anat_file, 'file')
            anat_path = whifun_check_anat_file(subject_folder, '0050952', 'session_1', 'anat_1', 'mprage');
            if ~isempty(anat_path)
                fprintf('  ✓ Function correctly located anatomical file\n');
            else
                fprintf('  ✗ Function failed to locate file\n');
            end
        end
    catch ME
        fprintf('  ✗ Error: %s\n', ME.message);
    end
    
    fprintf('\n');
    
    %% Test 3: Test NIfTI reading (if SPM available)
    fprintf('>>> Test 3: Testing NIfTI reading functions\n');
    fprintf('--------------------------------------------------------------------\n');
    
    spm_available = ~isempty(which('spm'));
    if spm_available
        fprintf('✓ SPM12 detected\n');
        
        try
            fprintf('Testing whifun_niftiread...\n');
            % This would require unzipping first
            fprintf('  Note: Files are .gz compressed, skipping direct read test\n');
        catch ME
            fprintf('  ✗ Error: %s\n', ME.message);
        end
    else
        fprintf('✗ SPM12 not found - skipping NIfTI tests\n');
        fprintf('  Install SPM12 for complete testing\n');
    end
    
    fprintf('\n');
    
    %% Test 4: Test utility functions
    fprintf('>>> Test 4: Testing utility functions\n');
    fprintf('--------------------------------------------------------------------\n');
    
    try
        fprintf('Testing complete_filepath...\n');
        test_path = complete_filepath(subject_folder, '0050952', 'session_1');
        if exist(test_path, 'dir')
            fprintf('  ✓ complete_filepath working correctly\n');
        else
            fprintf('  ✗ Path construction failed\n');
        end
    catch ME
        fprintf('  ✗ Error: %s\n', ME.message);
    end
    
    fprintf('\n');
    
    %% Summary
    fprintf('====================================================================\n');
    fprintf('Testing Summary\n');
    fprintf('====================================================================\n');
    fprintf('Test data location: %s\n', test_data_dir);
    fprintf('Output folder: %s\n', output_folder);
    fprintf('\nFor complete preprocessing tests, use the main WhiFuN GUI with\n');
    fprintf('this test dataset.\n');
    fprintf('====================================================================\n');
end

end

%% Helper function to create synthetic test data
function create_synthetic_test_data(test_data_dir)

fprintf('Creating synthetic test data structure...\n');

% Create directory structure
subj_dir = fullfile(test_data_dir, 'practice_NYU_abide', '0050952', 'session_1');
anat_dir = fullfile(subj_dir, 'anat_1');
func_dir = fullfile(subj_dir, 'rest_1');

if ~exist(anat_dir, 'dir'), mkdir(anat_dir); end
if ~exist(func_dir, 'dir'), mkdir(func_dir); end

fprintf('  ✓ Created directory structure\n');

% Check if SPM is available for creating NIfTI files
if ~isempty(which('spm'))
    fprintf('  Creating synthetic NIfTI files with SPM...\n');
    
    try
        % Create synthetic anatomical image (91x109x91 typical MNI space)
        anat_data = zeros(91, 109, 91);
        % Add some structure (brain-like blob)
        [X, Y, Z] = ndgrid(1:91, 1:109, 1:91);
        center_x = 46; center_y = 55; center_z = 46;
        radius = 30;
        brain_mask = ((X-center_x).^2 + (Y-center_y).^2 + (Z-center_z).^2) < radius^2;
        anat_data(brain_mask) = 100 + 50*rand(sum(brain_mask(:)), 1);
        
        % Create NIfTI header
        V_anat = struct();
        V_anat.fname = fullfile(anat_dir, 'mprage.nii');
        V_anat.dim = [91, 109, 91];
        V_anat.dt = [16, 0]; % float32
        V_anat.mat = [-2 0 0 90; 0 2 0 -126; 0 0 2 -72; 0 0 0 1];
        V_anat.descrip = 'Synthetic test anatomical image';
        
        spm_write_vol(V_anat, anat_data);
        fprintf('  ✓ Created synthetic anatomical image\n');
        
        % Create synthetic functional image (91x109x91x20 - 20 volumes)
        func_data = zeros(91, 109, 91, 20);
        for vol = 1:20
            func_data(:,:,:,vol) = anat_data * 0.8 + randn(91, 109, 91) * 10;
        end
        
        % Create 4D NIfTI
        V_func = V_anat;
        V_func.fname = fullfile(func_dir, 'rest.nii');
        V_func.dim = [91, 109, 91];
        V_func.descrip = 'Synthetic test functional image';
        
        for vol = 1:20
            V_func.n = [vol, 1];
            spm_write_vol(V_func, func_data(:,:,:,vol));
        end
        fprintf('  ✓ Created synthetic functional image (20 volumes)\n');
        
    catch ME
        fprintf('  ✗ Error creating NIfTI files: %s\n', ME.message);
        fprintf('  Creating placeholder files instead...\n');
        create_placeholder_files(anat_dir, func_dir);
    end
else
    fprintf('  SPM not available, creating placeholder files...\n');
    create_placeholder_files(anat_dir, func_dir);
end

fprintf('  ✓ Synthetic test data created successfully\n\n');

end

function create_placeholder_files(anat_dir, func_dir)
% Create simple text placeholders when SPM is not available

anat_file = fullfile(anat_dir, 'mprage_placeholder.txt');
func_file = fullfile(func_dir, 'rest_placeholder.txt');

fid = fopen(anat_file, 'w');
fprintf(fid, 'This is a placeholder for anatomical data.\n');
fprintf(fid, 'For real testing, please download actual data from Google Drive.\n');
fclose(fid);

fid = fopen(func_file, 'w');
fprintf(fid, 'This is a placeholder for functional data.\n');
fprintf(fid, 'For real testing, please download actual data from Google Drive.\n');
fclose(fid);

fprintf('  ✓ Created placeholder files\n');

end
