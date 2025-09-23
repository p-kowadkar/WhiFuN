# PyWhiFuN Dependency Map

This document tracks the conversion status of all functions called by the main `whifun_preprocess_script.m` pipeline and other key utilities.

## Core Pipeline Functions

| MATLAB Function                      | Purpose                                       | Python Equivalent / Status                 |
| ------------------------------------ | --------------------------------------------- | ------------------------------------------ |
| `load_subjects_all` / `load_subjects`| Loads and parses the `Subj_list.csv` file.    | Done (`load_subjects_from_csv`)            |
| `write_error`                        | Writes exception info to a log file.          | Done (`pywhifun.utils.logging`)            |
| `niftisave`                          | Saves a NIfTI file using a template.          | To Do (Blocked by nibabel issue)           |
| `whifun_realignment`                 | SPM wrapper for motion correction.            | To Do (map to `nilearn.image`)             |
| `whifun_segment`                     | SPM wrapper for tissue segmentation.          | To Do (map to `nilearn.image`)             |
| `whifun_skullstrip`                  | Creates a brain mask from segmented tissues.  | To Do (in `pywhifun.preprocessing.masking`)|
| `whifun_anat_mask`                   | Creates a specific anatomical mask.           | To Do (in `pywhifun.preprocessing.masking`)|
| `whifun_coreg`                       | SPM wrapper for coregistration.               | To Do (map to `nilearn.image`)             |
| `whifun_create_csf_mask`             | Creates a Cerebrospinal Fluid (CSF) mask.     | To Do (in `pywhifun.preprocessing.masking`)|
| `whifun_extract_csf_ts`              | Extracts time series from the CSF mask.       | To Do (in `pywhifun.preprocessing.timeseries`)|
| `whifun_regress`                     | Performs nuisance signal regression.          | To Do (in `pywhifun.preprocessing.regression`)|
| `p_smooth_WM_GM_separately_fast`     | Custom smoothing logic.                       | To Do (in `pywhifun.preprocessing.smoothing`)|
| `whifun_smooth_together`             | SPM wrapper for spatial smoothing.            | To Do (map to `nilearn.image.smooth_img`)  |
| `whifun_normalise`                   | SPM wrapper for spatial normalization.        | To Do (map to `nilearn.image.resample_to_img`)|
| `spm_check_registration_evalc`       | SPM function for QC plot generation.          | To Do (map to `nilearn.plotting`)          |
| `whifun_segment_qc`                  | Generates QC plots for segmentation.          | To Do (in `pywhifun.visualization.qc`)     |
| `whifun_ts_check`                    | Generates QC plots for time series.           | To Do (in `pywhifun.visualization.qc`)     |
| `my_writetable`                      | Saves a struct as a CSV file.                 | Done (`write_list_of_dicts_to_csv`)        |

## Other Converted Utility Functions

| MATLAB Function         | Purpose                                     | Python Equivalent / Status                |
| ----------------------- | ------------------------------------------- | ----------------------------------------- |
| `complete_filepath.m`   | Resolves file paths with wildcards.         | Done (`pywhifun.utils.path_utils`)        |
| `corrvec.m`             | Vectorizes a correlation matrix.            | Done (`pywhifun.utils.array_utils`)       |
| `dice_iou.m`            | Calculates Dice and IoU metrics.            | Done (`pywhifun.core.metrics`)            |
| `fd_calc.m`             | Calculates Framewise Displacement (L2 norm).| Done (`calculate_fd`)                     |
| FD from script          | Calculates FD using sum of differences.     | Done (`calculate_fd_sum`)                 |
| Unzip logic             | Decompresses .nii.gz files.                 | Done (`unzip_nifti_if_needed`)            |
| `fdr_bh.m`              | Performs FDR correction.                    | Done (`pywhifun.core.stats`)              |
| `fisherZ.m`             | Performs Fisher Z-transform.                | Done (`pywhifun.core.stats`)              |
| `functional_connectivity.m` | Calculates FC matrix from time series.      | Partial (`calculate_static_fc` is Done)   |
