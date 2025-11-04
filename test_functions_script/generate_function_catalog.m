%% GENERATE_FUNCTION_CATALOG - Creates a comprehensive catalog of all WhiFuN functions
%
%   This script generates a detailed catalog/documentation of all functions
%   in the WhiFuN toolbox, organized by category and functionality.
%
%   Output includes:
%   - Function name
%   - Location (root or whifun_functions)
%   - Brief description from help
%   - Input/output argument counts
%   - Function signature
%
%   Usage:
%       generate_function_catalog
%
%   Author: GitHub Copilot
%   Date: November 4, 2025

clc; clear; close all;

%% Setup
script_path = fileparts(mfilename('fullpath'));
whifun_root = fileparts(script_path);
addpath(genpath(whifun_root));

output_dir = fullfile(script_path, 'test_results');
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

timestamp = datestr(now, 'yyyymmdd_HHMMSS');
catalog_file = fullfile(output_dir, ['function_catalog_' timestamp '.txt']);
fid = fopen(catalog_file, 'w');

fprintf('Generating WhiFuN Function Catalog...\n');
fprintf(fid, '====================================================================\n');
fprintf(fid, 'WhiFuN Function Catalog\n');
fprintf(fid, 'Generated: %s\n', datestr(now));
fprintf(fid, '====================================================================\n\n');

%% Collect all functions
root_files = dir(fullfile(whifun_root, '*.m'));
func_files = dir(fullfile(whifun_root, 'whifun_functions', '*.m'));

% Categories
categories = struct();
categories.root = {};
categories.preprocessing = {};
categories.qc = {};
categories.network = {};
categories.utilities = {};
categories.io = {};
categories.statistics = {};
categories.visualization = {};
categories.other = {};

%% Process root level functions
fprintf('Processing root level functions...\n');
fprintf(fid, '====================================================================\n');
fprintf(fid, 'ROOT LEVEL FUNCTIONS\n');
fprintf(fid, '====================================================================\n\n');

root_count = 0;
for i = 1:length(root_files)
    fname = root_files(i).name;
    [~, func_name, ~] = fileparts(fname);
    full_path = fullfile(root_files(i).folder, fname);
    
    if contains(fname, {'script', 'Script'}, 'IgnoreCase', true) || ...
       contains(fname, '.asv')
        continue;
    end
    
    if is_function_file(full_path)
        root_count = root_count + 1;
        write_function_info(fid, func_name, full_path, 'Root');
        categories.root{end+1} = func_name; %#ok<SAGROW>
    end
end

fprintf(fid, '\nTotal Root Functions: %d\n\n', root_count);

%% Process whifun_functions folder
fprintf('Processing whifun_functions folder...\n');
fprintf(fid, '====================================================================\n');
fprintf(fid, 'WHIFUN_FUNCTIONS FOLDER\n');
fprintf(fid, '====================================================================\n\n');

func_count = 0;
for i = 1:length(func_files)
    fname = func_files(i).name;
    [~, func_name, ~] = fileparts(fname);
    full_path = fullfile(func_files(i).folder, fname);
    
    if is_function_file(full_path)
        func_count = func_count + 1;
        
        % Categorize
        if contains(func_name, {'preproc', 'segment', 'realign', 'coreg', 'normalise', 'smooth', 'filter', 'regress'}, 'IgnoreCase', true)
            categories.preprocessing{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, 'qc', 'IgnoreCase', true)
            categories.qc{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, {'FN', 'network', 'kmeans', 'cluster'}, 'IgnoreCase', true)
            categories.network{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, {'read', 'write', 'load', 'save', 'nifti'}, 'IgnoreCase', true)
            categories.io{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, {'stat', 'corr', 'fisher', 'partial'}, 'IgnoreCase', true)
            categories.statistics{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, {'view', 'display', 'plot', 'slover', 'brainnet'}, 'IgnoreCase', true)
            categories.visualization{end+1} = func_name; %#ok<SAGROW>
        elseif contains(func_name, {'create', 'build', 'get', 'extract', 'convert'}, 'IgnoreCase', true)
            categories.utilities{end+1} = func_name; %#ok<SAGROW>
        else
            categories.other{end+1} = func_name; %#ok<SAGROW>
        end
    end
end

fprintf(fid, '\nTotal whifun_functions: %d\n\n', func_count);

%% Write categorized summary
fprintf(fid, '====================================================================\n');
fprintf(fid, 'SUMMARY BY CATEGORY\n');
fprintf(fid, '====================================================================\n\n');

fprintf(fid, 'Root Functions: %d\n', length(categories.root));
fprintf(fid, 'Preprocessing Functions: %d\n', length(categories.preprocessing));
fprintf(fid, 'Quality Control Functions: %d\n', length(categories.qc));
fprintf(fid, 'Network Analysis Functions: %d\n', length(categories.network));
fprintf(fid, 'I/O Functions: %d\n', length(categories.io));
fprintf(fid, 'Statistics Functions: %d\n', length(categories.statistics));
fprintf(fid, 'Visualization Functions: %d\n', length(categories.visualization));
fprintf(fid, 'Utility Functions: %d\n', length(categories.utilities));
fprintf(fid, 'Other Functions: %d\n', length(categories.other));
fprintf(fid, '\nTotal: %d\n', root_count + func_count);

%% Write detailed categorized list
write_category_section(fid, 'PREPROCESSING FUNCTIONS', categories.preprocessing);
write_category_section(fid, 'QUALITY CONTROL FUNCTIONS', categories.qc);
write_category_section(fid, 'NETWORK ANALYSIS FUNCTIONS', categories.network);
write_category_section(fid, 'I/O FUNCTIONS', categories.io);
write_category_section(fid, 'STATISTICS FUNCTIONS', categories.statistics);
write_category_section(fid, 'VISUALIZATION FUNCTIONS', categories.visualization);
write_category_section(fid, 'UTILITY FUNCTIONS', categories.utilities);
write_category_section(fid, 'OTHER FUNCTIONS', categories.other);

fclose(fid);

fprintf('\nCatalog generated successfully!\n');
fprintf('Saved to: %s\n', catalog_file);
fprintf('\nTotal Functions: %d\n', root_count + func_count);

%% Helper Functions

function is_func = is_function_file(filepath)
    is_func = false;
    try
        fid = fopen(filepath, 'r');
        if fid == -1, return; end
        
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

function write_function_info(fid, func_name, full_path, location)
    fprintf(fid, '--------------------------------------------------------------------\n');
    fprintf(fid, 'Function: %s\n', func_name);
    fprintf(fid, 'Location: %s\n', location);
    
    % Get signature
    try
        fid2 = fopen(full_path, 'r');
        while ~feof(fid2)
            line = strtrim(fgetl(fid2));
            if isempty(line) || startsWith(line, '%')
                continue;
            end
            if startsWith(line, 'function')
                fprintf(fid, 'Signature: %s\n', line);
                break;
            end
        end
        fclose(fid2);
    catch
    end
    
    % Get help (first line only)
    try
        help_text = help(func_name);
        if ~isempty(strtrim(help_text)) && ~contains(help_text, 'not found')
            lines = splitlines(help_text);
            if ~isempty(lines)
                fprintf(fid, 'Description: %s\n', strtrim(lines{1}));
            end
        end
    catch
    end
    
    % Get arg counts
    try
        nin = nargin(func_name);
        nout = nargout(func_name);
        fprintf(fid, 'Arguments: %d in, %d out\n', nin, nout);
    catch
    end
    
    fprintf(fid, '\n');
end

function write_category_section(fid, title, func_list)
    fprintf(fid, '\n====================================================================\n');
    fprintf(fid, '%s (%d)\n', title, length(func_list));
    fprintf(fid, '====================================================================\n\n');
    
    if isempty(func_list)
        fprintf(fid, '(None)\n\n');
        return;
    end
    
    func_list = sort(func_list);
    for i = 1:length(func_list)
        fprintf(fid, '%3d. %s\n', i, func_list{i});
    end
    fprintf(fid, '\n');
end
