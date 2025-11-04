%% RUN_ALL_TESTS - Master script to run all WhiFuN function tests
%
%   This script runs all available test scripts in sequence:
%   1. Quick test for immediate issues
%   2. Comprehensive function testing
%   3. Function catalog generation
%
%   Usage:
%       run_all_tests
%
%   Author: GitHub Copilot
%   Date: November 4, 2025

clc; clear; close all;

fprintf('====================================================================\n');
fprintf('WhiFuN Function Testing Suite - Complete Run\n');
fprintf('====================================================================\n\n');

start_time = tic;

%% Test 1: Quick validation
fprintf('>>> Step 1/3: Running quick validation test...\n');
fprintf('--------------------------------------------------------------------\n');
try
    quick_test_functions;
    fprintf('✓ Quick test completed\n\n');
catch ME
    fprintf('✗ Quick test failed: %s\n\n', ME.message);
end

fprintf('Press any key to continue to comprehensive testing...\n');
pause;

%% Test 2: Comprehensive testing
fprintf('\n>>> Step 2/3: Running comprehensive function tests...\n');
fprintf('--------------------------------------------------------------------\n');
try
    test_all_whifun_functions;
    fprintf('✓ Comprehensive test completed\n\n');
catch ME
    fprintf('✗ Comprehensive test failed: %s\n\n', ME.message);
end

fprintf('Press any key to continue to catalog generation...\n');
pause;

%% Test 3: Generate catalog
fprintf('\n>>> Step 3/3: Generating function catalog...\n');
fprintf('--------------------------------------------------------------------\n');
try
    generate_function_catalog;
    fprintf('✓ Catalog generation completed\n\n');
catch ME
    fprintf('✗ Catalog generation failed: %s\n\n', ME.message);
end

%% Summary
elapsed_time = toc(start_time);

fprintf('\n====================================================================\n');
fprintf('All Tests Completed\n');
fprintf('====================================================================\n');
fprintf('Total time: %.2f seconds (%.2f minutes)\n', elapsed_time, elapsed_time/60);
fprintf('\nAll results saved in: test_functions_script/test_results/\n');
fprintf('====================================================================\n');
