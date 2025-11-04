%% START_TESTING - Quick launcher for WhiFuN function tests
%
%   This script provides an interactive menu to launch different tests.

clc; clear; close all;

fprintf('====================================================================\n');
fprintf('     WhiFuN Function Testing Suite - Interactive Launcher\n');
fprintf('====================================================================\n\n');

while true
    fprintf('Available Tests:\n\n');
    fprintf('  1. Quick Test (30-60 seconds)\n');
    fprintf('  2. Comprehensive Test (2-5 minutes)\n');
    fprintf('  3. Test Individual Function\n');
    fprintf('  4. Generate Function Catalog\n');
    fprintf('  5. Run All Tests\n');
    fprintf('  6. View Examples\n');
    fprintf('  0. Exit\n\n');
    
    choice = input('Select option (0-6): ', 's');
    
    fprintf('\n');
    
    switch choice
        case '1'
            fprintf('Running Quick Test...\n');
            fprintf('--------------------------------------------------------------------\n');
            quick_test_functions;
            
        case '2'
            fprintf('Running Comprehensive Test...\n');
            fprintf('--------------------------------------------------------------------\n');
            test_all_whifun_functions;
            
        case '3'
            func_name = input('Enter function name to test: ', 's');
            if ~isempty(func_name)
                fprintf('Testing %s...\n', func_name);
                fprintf('--------------------------------------------------------------------\n');
                test_individual_function(func_name);
            else
                fprintf('No function name provided.\n');
            end
            
        case '4'
            fprintf('Generating Function Catalog...\n');
            fprintf('--------------------------------------------------------------------\n');
            generate_function_catalog;
            
        case '5'
            fprintf('Running All Tests...\n');
            fprintf('--------------------------------------------------------------------\n');
            run_all_tests;
            
        case '6'
            fprintf('Opening example_usage.m...\n');
            edit example_usage.m;
            
        case '0'
            fprintf('Exiting...\n');
            break;
            
        otherwise
            fprintf('Invalid choice. Please select 0-6.\n');
    end
    
    if ~strcmp(choice, '0')
        fprintf('\n');
        input('Press Enter to return to menu...', 's');
        clc;
        fprintf('====================================================================\n');
        fprintf('     WhiFuN Function Testing Suite - Interactive Launcher\n');
        fprintf('====================================================================\n\n');
    end
end

fprintf('====================================================================\n');
fprintf('Thank you for using the WhiFuN Testing Suite!\n');
fprintf('====================================================================\n');
