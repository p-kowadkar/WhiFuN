# WhiFuN Function Testing Suite

This folder contains scripts to test and validate all functions in the WhiFuN toolbox.

## Test Scripts

### 1. `test_all_whifun_functions.m`
**Comprehensive testing of all WhiFuN functions**

Tests all functions in:
- Root level (e.g., `whifun.m`, `whifun_dartel.m`)
- `whifun_functions/` folder

**What it tests:**
- Function existence and accessibility
- Help documentation presence and quality
- Input/output argument counts
- Function signatures
- Basic syntax validation

**Usage:**
```matlab
cd test_functions_script
test_all_whifun_functions
```

**Output:**
- Detailed log file in `test_results/test_log_YYYYMMDD_HHMMSS.txt`
- MAT file with test results for further analysis
- Console summary with pass/fail statistics

**Time:** ~2-5 minutes depending on number of functions

---

### 2. `test_individual_function.m`
**Detailed testing of a specific function**

Performs in-depth analysis on a single function including:
- Help documentation
- Function signature
- Code metrics (lines of code, comments, etc.)
- Dependencies and required products

**Usage:**
```matlab
cd test_functions_script
test_individual_function('whifun_preproc')
test_individual_function('whifun_create_FN_Kmeans')
```

**Output:**
- Detailed console output with all metrics
- Dependency tree

**Time:** ~5-30 seconds per function

---

### 3. `quick_test_functions.m`
**Fast sanity check of all functions**

Quick validation to identify immediate issues:
- File accessibility
- Basic function structure
- Help documentation presence

**Usage:**
```matlab
cd test_functions_script
quick_test_functions
```

**Output:**
- Quick summary to console
- List of issues found

**Time:** ~30-60 seconds

---

### 4. `test_with_google_drive_data.m`
**Test functions with real practice data**

Tests WhiFuN functions using the practice dataset from Google Drive.
Provides options for:
- Manual data download instructions
- Synthetic test data generation
- Real function testing with actual neuroimaging data

**Usage:**
```matlab
cd test_functions_script
test_with_google_drive_data              % Full test with data
test_with_google_drive_data('download_only')   % Setup only
test_with_google_drive_data('test_functions')  % Test with existing data
```

**Requirements:**
- Internet connection (for data download)
- SPM12 (optional, for synthetic data generation)
- Practice data from: https://drive.google.com/drive/folders/1l7dhG8dYYRCW5EWhkPZbBpA7TOau1W-B

**What it tests:**
- File location functions (`whifun_check_func_file`, `whifun_check_anat_file`)
- Path construction utilities
- NIfTI reading capabilities
- Data structure validation

**Output:**
- Test results to console
- Test data cached in `temp_test_data/` folder

**Time:** Variable (depends on data download)

---

## Typical Workflow

1. **First run:** Use `quick_test_functions` to get a quick overview
2. **Detailed analysis:** Run `test_all_whifun_functions` for comprehensive testing
3. **Debug specific issues:** Use `test_individual_function` to investigate problem functions

## Test Results

All test results are saved in the `test_results/` folder with timestamps:
- `test_log_YYYYMMDD_HHMMSS.txt` - Detailed text log
- `test_results_YYYYMMDD_HHMMSS.mat` - MATLAB data for analysis

## What Gets Tested

### Root Level Functions:
- `whifun.m` - Main GUI launcher
- `whifun_dartel.m` - DARTEL template creation
- `whifun_dartel_normalize_smooth.m` - DARTEL normalization
- `whifun_addpath_and_create_preproc_folders.m` - Setup utility

### whifun_functions/ Folder:
All ~130+ functions including:
- Preprocessing functions (`whifun_preproc.m`, `whifun_segment.m`, etc.)
- QC functions (`whifun_qc*.m`)
- Network creation (`whifun_create_FN_Kmeans.m`, `whifun_get_FN_kmeans.m`)
- Utility functions (file I/O, mask creation, etc.)

### What Gets Skipped:
- Script files (e.g., `whifun_preprocess_script.m`)
- MATLAB App files (`.mlapp`)
- Backup files (`.asv`)
- Non-function files

## Interpreting Results

### Status Indicators:
- **[PASS]** - Function works correctly
- **[WARNING]** - Function works but has minor issues (e.g., missing help)
- **[FAIL]** - Function has errors or cannot be loaded

### Common Issues:
1. **No help documentation** - Function works but lacks help text
2. **Cannot determine arg counts** - Functions with `varargin`/`varargout`
3. **File not accessible** - Path or permission issues

## Examples

### Run comprehensive test:
```matlab
cd d:\MyProject\WhiFuN-1\test_functions_script
test_all_whifun_functions
```

### Test a specific function:
```matlab
test_individual_function('whifun_preproc')
```

### Quick check:
```matlab
quick_test_functions
```

## Notes

- These tests do NOT execute functions (no functional testing)
- Tests check structure, documentation, and basic validity
- No data or SPM12 required to run tests
- Safe to run without affecting any data

## Author
Created for WhiFuN v3 testing and validation
Date: November 4, 2025
