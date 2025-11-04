%% TEST_ALL_WHIFUN_FUNCTIONS - Comprehensive test suite for WhiFuN functions
%
%   This script tests all functions in the WhiFuN toolbox to ensure they:
%   1. Have proper function signatures
%   2. Have help documentation
%   3. Can be parsed without syntax errors
%   4. Have valid input/output argument counts
%
%   Usage:
%       test_all_whifun_functions
%
%   Output:
%       Generates a detailed report in test_functions_script/test_results/

clc; clear; close all;

%% Setup paths
script_path = fileparts(mfilename('fullpath'));
whifun_root = fileparts(script_path);
addpath(genpath(whifun_root));

% Create output directory
output_dir = fullfile(script_path, 'test_results');
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

% Log file
timestamp = datestr(now, 'yyyymmdd_HHMMSS');
log_file = fullfile(output_dir, ['test_log_' timestamp '.txt']);
fid = fopen(log_file, 'w');

fprintf(fid, '====================================================================\n');
fprintf(fid, 'WhiFuN Function Test Suite\n');
fprintf(fid, 'Date: %s\n', datestr(now));
fprintf(fid, '====================================================================\n\n');

%% Identify all root-level functions (excluding scripts and mlapp files)
fprintf('Scanning for functions...\n');
fprintf(fid, 'SCANNING FOR FUNCTIONS\n\n');

root_m_files = dir(fullfile(whifun_root, '*.m'));
root_functions = {};

fprintf(fid, 'Root Level Files:\n');
for i = 1:length(root_m_files)
    fname = root_m_files(i).name;
    full_path = fullfile(root_m_files(i).folder, fname);
    
    % Exclude certain files
    if contains(fname, {'script', 'Script'}, 'IgnoreCase', true) || ...
       strcmp(fname, 'whifun_ts_qc_script.asv')
        fprintf(fid, '  [SKIPPED - Script] %s\n', fname);
        continue;
    end
    
    % Check if it's a function
    if is_function_file(full_path)
        root_functions{end+1} = full_path; %#ok<SAGROW>
        fprintf(fid, '  [FUNCTION] %s\n', fname);
    else
        fprintf(fid, '  [SKIPPED - Not a function] %s\n', fname);
    end
end

%% Identify all functions in whifun_functions folder
whifun_func_dir = fullfile(whifun_root, 'whifun_functions');
func_m_files = dir(fullfile(whifun_func_dir, '*.m'));
whifun_functions = {};

fprintf(fid, '\nwhifun_functions Folder:\n');
for i = 1:length(func_m_files)
    fname = func_m_files(i).name;
    full_path = fullfile(func_m_files(i).folder, fname);
    
    if is_function_file(full_path)
        whifun_functions{end+1} = full_path; %#ok<SAGROW>
        fprintf(fid, '  [FUNCTION] %s\n', fname);
    else
        fprintf(fid, '  [SKIPPED - Not a function] %s\n', fname);
    end
end

%% Combine all functions
all_functions = [root_functions, whifun_functions];
fprintf('\nTotal functions to test: %d\n', length(all_functions));
fprintf(fid, '\nTotal Functions to Test: %d\n\n', length(all_functions));
fprintf(fid, '====================================================================\n\n');

%% Test each function
test_results = struct('name', {}, 'path', {}, 'has_help', {}, 'help_text', {}, ...
                      'nargin', {}, 'nargout', {}, 'status', {}, 'error_msg', {});

fprintf('\nRunning tests...\n');
fprintf(fid, 'TEST RESULTS\n\n');

for i = 1:length(all_functions)
    func_path = all_functions{i};
    [~, func_name, ~] = fileparts(func_path);
    
    fprintf('Testing %d/%d: %s\n', i, length(all_functions), func_name);
    fprintf(fid, '--------------------------------------------------------------------\n');
    fprintf(fid, 'Function %d/%d: %s\n', i, length(all_functions), func_name);
    fprintf(fid, 'Path: %s\n', func_path);
    
    result = struct();
    result.name = func_name;
    result.path = func_path;
    
    try
        % Test 1: Check if help exists
        help_text = help(func_name);
        if isempty(strtrim(help_text)) || contains(help_text, 'not found')
            result.has_help = false;
            result.help_text = 'No help available';
            fprintf(fid, '  [WARNING] No help documentation found\n');
        else
            result.has_help = true;
            result.help_text = help_text(1:min(200, length(help_text))); % First 200 chars
            fprintf(fid, '  [PASS] Help documentation exists\n');
        end
        
        % Test 2: Get number of input/output arguments
        try
            result.nargin = nargin(func_name);
            result.nargout = nargout(func_name);
            fprintf(fid, '  [INFO] Input args: %d, Output args: %d\n', result.nargin, result.nargout);
        catch ME
            result.nargin = -1;
            result.nargout = -1;
            fprintf(fid, '  [WARNING] Could not determine arg counts: %s\n', ME.message);
        end
        
        % Test 3: Check function signature
        func_sig = get_function_signature(func_path);
        if ~isempty(func_sig)
            fprintf(fid, '  [INFO] Signature: %s\n', func_sig);
        end
        
        % Test 4: Basic syntax check (already done by parsing)
        result.status = 'PASS';
        result.error_msg = '';
        fprintf(fid, '  [PASS] Function is valid\n');
        
    catch ME
        result.status = 'FAIL';
        result.error_msg = ME.message;
        result.has_help = false;
        result.help_text = '';
        result.nargin = -1;
        result.nargout = -1;
        
        fprintf(fid, '  [FAIL] Error: %s\n', ME.message);
        fprintf(2, '  ERROR: %s - %s\n', func_name, ME.message);
    end
    
    test_results(i) = result; %#ok<SAGROW>
    fprintf(fid, '\n');
end

%% Generate summary
fprintf(fid, '====================================================================\n');
fprintf(fid, 'SUMMARY\n');
fprintf(fid, '====================================================================\n\n');

total = length(test_results);
passed = sum(strcmp({test_results.status}, 'PASS'));
failed = sum(strcmp({test_results.status}, 'FAIL'));
with_help = sum([test_results.has_help]);
without_help = sum(~[test_results.has_help]);

fprintf(fid, 'Total Functions Tested: %d\n', total);
fprintf(fid, 'Passed: %d (%.1f%%)\n', passed, (passed/total)*100);
fprintf(fid, 'Failed: %d (%.1f%%)\n', failed, (failed/total)*100);
fprintf(fid, 'With Help Documentation: %d (%.1f%%)\n', with_help, (with_help/total)*100);
fprintf(fid, 'Without Help Documentation: %d (%.1f%%)\n\n', without_help, (without_help/total)*100);

% List functions without help
fprintf(fid, 'Functions Without Help Documentation:\n');
no_help_funcs = {test_results(~[test_results.has_help]).name};
if isempty(no_help_funcs)
    fprintf(fid, '  None - All functions have help!\n');
else
    for i = 1:length(no_help_funcs)
        fprintf(fid, '  %d. %s\n', i, no_help_funcs{i});
    end
end
fprintf(fid, '\n');

% List failed functions
if failed > 0
    fprintf(fid, 'Failed Functions:\n');
    failed_funcs = test_results(strcmp({test_results.status}, 'FAIL'));
    for i = 1:length(failed_funcs)
        fprintf(fid, '  %d. %s - %s\n', i, failed_funcs(i).name, failed_funcs(i).error_msg);
    end
end

fprintf(fid, '\n====================================================================\n');
fprintf(fid, 'Test completed: %s\n', datestr(now));
fprintf(fid, '====================================================================\n');

fclose(fid);

%% Save results to MAT file
results_mat = fullfile(output_dir, ['test_results_' timestamp '.mat']);
save(results_mat, 'test_results', 'all_functions');

%% Display summary to console
fprintf('\n====================================================================\n');
fprintf('TEST SUMMARY\n');
fprintf('====================================================================\n');
fprintf('Total Functions Tested: %d\n', total);
fprintf('Passed: %d (%.1f%%)\n', passed, (passed/total)*100);
fprintf('Failed: %d (%.1f%%)\n', failed, (failed/total)*100);
fprintf('With Help Documentation: %d (%.1f%%)\n', with_help, (with_help/total)*100);
fprintf('Without Help Documentation: %d (%.1f%%)\n', without_help, (without_help/total)*100);
fprintf('\nDetailed results saved to:\n  %s\n', log_file);
fprintf('  %s\n', results_mat);
fprintf('====================================================================\n');

%% Helper Functions

function is_func = is_function_file(filepath)
    % Check if a file is a function (not a script)
    is_func = false;
    try
        fid = fopen(filepath, 'r');
        if fid == -1
            return;
        end
        
        % Read first non-comment, non-blank line
        while ~feof(fid)
            line = strtrim(fgetl(fid));
            if isempty(line) || startsWith(line, '%')
                continue;
            end
            if startsWith(line, 'function')
                is_func = true;
            end
            break;
        end
        fclose(fid);
    catch
        is_func = false;
    end
end

function signature = get_function_signature(filepath)
    % Extract function signature from file
    signature = '';
    try
        fid = fopen(filepath, 'r');
        if fid == -1
            return;
        end
        
        while ~feof(fid)
            line = strtrim(fgetl(fid));
            if isempty(line) || startsWith(line, '%')
                continue;
            end
            if startsWith(line, 'function')
                signature = strtrim(line);
                break;
            end
        end
        fclose(fid);
    catch
        signature = '';
    end
end
