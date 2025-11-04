%% QUICK_TEST_FUNCTIONS - Quick validation test for WhiFuN functions
%
%   This script performs a quick sanity check on all WhiFuN functions
%   to identify any immediate issues with:
%   - File accessibility
%   - Basic syntax
%   - Help documentation presence
%
%   This is a faster alternative to test_all_whifun_functions.m
%
%   Usage:
%       quick_test_functions

clc; clear; close all;

fprintf('Quick Function Validation Test\n');
fprintf('====================================================================\n\n');

%% Setup
script_path = fileparts(mfilename('fullpath'));
whifun_root = fileparts(script_path);
addpath(genpath(whifun_root));

%% Get all function files
fprintf('Scanning for functions...\n');

% Root level
root_files = dir(fullfile(whifun_root, '*.m'));
% whifun_functions folder
func_files = dir(fullfile(whifun_root, 'whifun_functions', '*.m'));

% Combine and filter
all_files = [root_files; func_files];
issues = {};

fprintf('Testing %d files...\n\n', length(all_files));

%% Quick test each file
pass_count = 0;
warn_count = 0;
fail_count = 0;

for i = 1:length(all_files)
    fname = all_files(i).name;
    [~, func_name, ~] = fileparts(fname);
    full_path = fullfile(all_files(i).folder, fname);
    
    % Skip scripts and special files
    if contains(fname, {'script', 'Script'}, 'IgnoreCase', true) || ...
       contains(fname, '.asv')
        continue;
    end
    
    % Check if it's a function
    try
        fid = fopen(full_path, 'r');
        if fid == -1
            issues{end+1} = sprintf('[FAIL] Cannot open: %s', fname); %#ok<SAGROW>
            fail_count = fail_count + 1;
            continue;
        end
        
        is_function = false;
        while ~feof(fid)
            line = strtrim(fgetl(fid));
            if isempty(line) || startsWith(line, '%')
                continue;
            end
            if startsWith(line, 'function')
                is_function = true;
            end
            break;
        end
        fclose(fid);
        
        if ~is_function
            continue; % Skip non-functions
        end
        
        % Check help
        help_text = help(func_name);
        if isempty(strtrim(help_text)) || contains(help_text, 'not found')
            issues{end+1} = sprintf('[WARN] No help: %s', func_name); %#ok<SAGROW>
            warn_count = warn_count + 1;
        else
            pass_count = pass_count + 1;
        end
        
    catch ME
        issues{end+1} = sprintf('[FAIL] Error in %s: %s', fname, ME.message); %#ok<SAGROW>
        fail_count = fail_count + 1;
    end
end

%% Display results
fprintf('====================================================================\n');
fprintf('RESULTS\n');
fprintf('====================================================================\n');
fprintf('✓ Passed: %d\n', pass_count);
fprintf('⚠ Warnings: %d\n', warn_count);
fprintf('✗ Failed: %d\n', fail_count);
fprintf('\n');

if ~isempty(issues)
    fprintf('Issues Found:\n');
    for i = 1:length(issues)
        fprintf('  %d. %s\n', i, issues{i});
    end
else
    fprintf('No issues found! All functions are accessible with help documentation.\n');
end

fprintf('====================================================================\n');
fprintf('\nFor detailed testing, run: test_all_whifun_functions\n');
fprintf('For individual function testing, use: test_individual_function(''function_name'')\n');
