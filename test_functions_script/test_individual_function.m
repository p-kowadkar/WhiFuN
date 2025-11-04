function test_individual_function(function_name)
%TEST_INDIVIDUAL_FUNCTION Tests a specific WhiFuN function in detail
%
%   test_individual_function(function_name) performs detailed testing on a
%   specific function including:
%   - Help documentation check
%   - Input/output argument validation
%   - Function signature extraction
%   - Code complexity analysis
%
%   Usage:
%       test_individual_function('whifun_preproc')
%       test_individual_function('whifun_create_FN_Kmeans')
%
%   Author: GitHub Copilot
%   Date: November 4, 2025

if nargin < 1
    error('Please provide a function name to test');
end

fprintf('====================================================================\n');
fprintf('Testing Function: %s\n', function_name);
fprintf('====================================================================\n\n');

%% Test 1: Function Exists
fprintf('1. Checking if function exists...\n');
func_path = which(function_name);
if isempty(func_path)
    fprintf('   [FAIL] Function not found in MATLAB path\n');
    return;
else
    fprintf('   [PASS] Function found at: %s\n', func_path);
end

%% Test 2: Help Documentation
fprintf('\n2. Checking help documentation...\n');
help_text = help(function_name);
if isempty(strtrim(help_text)) || contains(help_text, 'not found')
    fprintf('   [FAIL] No help documentation available\n');
else
    fprintf('   [PASS] Help documentation exists\n');
    fprintf('   First 300 characters:\n');
    fprintf('   %s...\n', help_text(1:min(300, length(help_text))));
end

%% Test 3: Input/Output Arguments
fprintf('\n3. Checking function signature...\n');
try
    nin = nargin(function_name);
    nout = nargout(function_name);
    fprintf('   [PASS] Number of input arguments: %d\n', nin);
    fprintf('   [PASS] Number of output arguments: %d\n', nout);
catch ME
    fprintf('   [WARNING] Could not determine arg counts: %s\n', ME.message);
end

%% Test 4: Function Signature
fprintf('\n4. Extracting function signature...\n');
try
    fid = fopen(func_path, 'r');
    signature_found = false;
    while ~feof(fid)
        line = strtrim(fgetl(fid));
        if isempty(line) || startsWith(line, '%')
            continue;
        end
        if startsWith(line, 'function')
            fprintf('   [PASS] Signature: %s\n', line);
            signature_found = true;
            break;
        end
    end
    fclose(fid);
    
    if ~signature_found
        fprintf('   [WARNING] Could not extract function signature\n');
    end
catch ME
    fprintf('   [FAIL] Error reading file: %s\n', ME.message);
end

%% Test 5: Code Analysis
fprintf('\n5. Analyzing code...\n');
try
    % Count lines of code
    fid = fopen(func_path, 'r');
    total_lines = 0;
    comment_lines = 0;
    code_lines = 0;
    blank_lines = 0;
    
    while ~feof(fid)
        line = fgetl(fid);
        total_lines = total_lines + 1;
        trimmed = strtrim(line);
        
        if isempty(trimmed)
            blank_lines = blank_lines + 1;
        elseif startsWith(trimmed, '%')
            comment_lines = comment_lines + 1;
        else
            code_lines = code_lines + 1;
        end
    end
    fclose(fid);
    
    fprintf('   Total lines: %d\n', total_lines);
    fprintf('   Code lines: %d (%.1f%%)\n', code_lines, (code_lines/total_lines)*100);
    fprintf('   Comment lines: %d (%.1f%%)\n', comment_lines, (comment_lines/total_lines)*100);
    fprintf('   Blank lines: %d (%.1f%%)\n', blank_lines, (blank_lines/total_lines)*100);
    
catch ME
    fprintf('   [WARNING] Code analysis failed: %s\n', ME.message);
end

%% Test 6: Dependencies
fprintf('\n6. Checking dependencies...\n');
try
    [fList, pList] = matlab.codetools.requiredFilesAndProducts(func_path);
    
    fprintf('   Required MATLAB files: %d\n', length(fList));
    if length(fList) <= 10
        for i = 1:length(fList)
            [~, fname, fext] = fileparts(fList{i});
            fprintf('     - %s%s\n', fname, fext);
        end
    else
        fprintf('     (showing first 10)\n');
        for i = 1:10
            [~, fname, fext] = fileparts(fList{i});
            fprintf('     - %s%s\n', fname, fext);
        end
        fprintf('     ... and %d more\n', length(fList)-10);
    end
    
    fprintf('   Required MATLAB products: %d\n', length(pList));
    for i = 1:length(pList)
        fprintf('     - %s\n', pList(i).Name);
    end
    
catch ME
    fprintf('   [WARNING] Dependency check failed: %s\n', ME.message);
end

fprintf('\n====================================================================\n');
fprintf('Test Complete\n');
fprintf('====================================================================\n');

end
