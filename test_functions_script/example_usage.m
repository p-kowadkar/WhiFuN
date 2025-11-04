%% EXAMPLE_USAGE - Demonstrates how to use the testing scripts
%
%   This script shows examples of how to use each testing utility.

%% Example 1: Quick Test
% Use this for a fast sanity check
clc; clear;
fprintf('=== Example 1: Quick Test ===\n\n');
quick_test_functions;

%% Example 2: Test a Specific Function
% Use this to examine a particular function in detail
clc; clear;
fprintf('=== Example 2: Individual Function Test ===\n\n');
test_individual_function('whifun_preproc');

%% Example 3: Test Another Function
clc; clear;
fprintf('=== Example 3: Testing Network Creation Function ===\n\n');
test_individual_function('whifun_create_FN_Kmeans');

%% Example 4: Comprehensive Testing
% This takes longer but tests everything
clc; clear;
fprintf('=== Example 4: Comprehensive Test ===\n\n');
fprintf('This will test all functions and generate a detailed report.\n');
fprintf('Continue? (Press any key or Ctrl+C to cancel)\n');
pause;
test_all_whifun_functions;

%% Example 5: Generate Function Catalog
% Creates a reference document of all functions
clc; clear;
fprintf('=== Example 5: Generate Catalog ===\n\n');
generate_function_catalog;

%% Example 6: Run Everything
% Master script that runs all tests
clc; clear;
fprintf('=== Example 6: Run All Tests ===\n\n');
fprintf('This will run all tests in sequence.\n');
fprintf('Continue? (Press any key or Ctrl+C to cancel)\n');
pause;
run_all_tests;

%% Tips
clc;
fprintf('====================================================================\n');
fprintf('TIPS FOR USING THE TEST SUITE\n');
fprintf('====================================================================\n\n');

fprintf('Quick Daily Check:\n');
fprintf('  >> quick_test_functions\n\n');

fprintf('Before Making Changes:\n');
fprintf('  >> test_all_whifun_functions\n');
fprintf('  (creates baseline for comparison)\n\n');

fprintf('After Modifying a Function:\n');
fprintf('  >> test_individual_function(''your_function_name'')\n\n');

fprintf('Generate Documentation:\n');
fprintf('  >> generate_function_catalog\n\n');

fprintf('Complete Validation:\n');
fprintf('  >> run_all_tests\n\n');

fprintf('====================================================================\n');
