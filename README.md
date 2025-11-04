# WhiFuN Version 3

We are open to feedback and comments. Please reach out if you get any issues, email: (jainpratik412[at]gmail[dot]com).

This GUI-based toolbox offers researchers a user-friendly suite of automated tools for investigating brain functional connectivity in White Matter (WM) and Gray Matter (GM). One of the key advantages of WhiFuN is that it fully automates the preprocessing steps to derive data that can be used to analyze the WM and GM BOLD signals.

## Citation

If you use WhiFuN in your research, please cite:

Pratik Jain, Andrew M. Michael, Pan Wang, Xin Di, Bharat Biswal; WhiFuN: A toolbox to map the white matter functional networks of the human brain. *Imaging Neuroscience* 2025; doi: https://doi.org/10.1162/IMAG.a.3

## What's new in version 3?

1) **Simplified scripting with single-function preprocessing**: All preprocessing can now be done with the single `whifun_preproc` function. Network creation has been streamlined with the `whifun_create_FN_Kmeans` function.

2) **Self-documented functions**: All functions in the WhiFuN toolbox now follow MATLAB documentation standards. To get detailed explanations of any function, its input arguments, output arguments, and dependencies, use:
   ```matlab
   >> help whifun_preproc
   >> help whifun_create_FN_Kmeans
   >> help whifun_using_other_preproc
   ```

3) **Enhanced Quality Control with Seed-Based Correlation Maps**: New QC plots include seed-based correlation maps for three major networks in Gray Matter:
   - Default Mode Network (DMN) - Seed at MNI coordinates (5, -49, 40) in left Posterior Cingulate Cortex
   - Visual Network - Seed at MNI coordinates (-4, -91, -3) in visual cortex
   - Auditory Network - Seed at MNI coordinates (64, -12, 2) in auditory cortex
   
   These plots help identify participants with poor data quality before network analysis.

4) **Integration with External Preprocessing Pipelines**: Data preprocessed using other toolboxes (fMRIPrep, CONN, DPARSF, etc.) can now be used with WhiFuN. Use the `whifun_using_other_preproc` function to create WM and GM Functional Networks from externally preprocessed data.

5) **DARTEL-based normalization**: Added support for DARTEL (Diffeomorphic Anatomical Registration Through Exponentiated Lie Algebra) for improved registration to MNI space. DARTEL provides more accurate inter-participant alignment compared to standard normalization.

6) **Input parser for robust parameter handling**: All preprocessing functions now use MATLAB's `inputParser` for clearer, more flexible parameter specification with better error checking.


## Requirements

WhiFuN is based on MATLAB; hence, it will not work if MATLAB is not installed. 
MATLAB R2022a or later versions are recommended.

**Required MATLAB Toolboxes:**
1) Image Processing Toolbox
2) Signal Processing Toolbox
3) Statistics and Machine Learning Toolbox
4) Bioinformatics Toolbox

**Required External Software:**
1) SPM12 (must be downloaded separately from https://www.fil.ion.ucl.ac.uk/spm/software/download/)

**Optional:**
1) Parallel Computing Toolbox (for faster processing)
2) AFNI (for advanced coregistration options)

These MATLAB toolboxes can be downloaded by using the Add-ons feature in MATLAB. More details here: https://www.mathworks.com/help/matlab/matlab_env/get-add-ons.html


## Getting Started with WhiFuN

### Installation Steps

1) Download WhiFuN in a local folder and unzip all the contents (Download WhiFuN by clicking on the green 'Code' button and then selecting Download zip, the toolbox will take about 24MB of disk space)

2) Open MATLAB and add the WhiFuN toolbox to MATLAB path
   
     i) by using the addpath function: Type the following in the MATLAB command window and press enter.
   
         addpath('<path to the WhiFuN folder>\WhiFuN')  
   
   or
   
     ii) Click _Home_ when you are on the main screen of MATLAB (top left), and then under the Environment section, click on _Set Path_. Next, click on _Add Folder_, select the WhiFuN folder with the _whifun.m_ code and click on _Select Folder_. Finally, click _Save_ and then _Close_.

3) If SPM12 toolbox is not downloaded, please download the SPM12 toolbox from https://www.fil.ion.ucl.ac.uk/spm/software/download/, and add the SPM toolbox path to MATLAB
   
     i) by using the addpath function: Type in the MATLAB command window and press enter.

          addpath('<path to the SPM folder>\spm12') 
   
   or
   
     ii) Click _Home_ when you are on the main screen of MATLAB (top left), and then under the Environment section, click on _Set Path_. Next, click on _Add Folder_, select the SPM folder with the _spm.m_ code, and click _Select Folder_. Finally, click _Save_ and then _Close_.

4) Once all the paths are set, type _whifun_ in the MATLAB command window and press enter.

5) The main GUI window of WhiFuN will open.

### Using the WhiFuN GUI

   i) Now, first, select the _Outputs Folder_ button and select an empty folder where all the outputs and quality control plots will be saved. Alternatively, one can paste the path of the output folder in the text field beside the _Outputs Folder_ button.

   ii) Click the _Participant Data Folder_ button and select the folder with all the participants' folders. As an example, we show how WhiFuN can be used with some practice data that can be downloaded here https://drive.google.com/drive/folders/1l7dhG8dYYRCW5EWhkPZbBpA7TOau1W-B?usp=sharing . Download the practice data, unzip the contents, and select the folder 'practice_NYU_abide' using the _Participant Data Folder button_ or paste the complete path. Please see the example screenshot below.
    
<img width="942" height="817" alt="Screenshot 2025-07-19 103118" src="https://github.com/user-attachments/assets/1e2dcc53-3d32-4ced-9546-6277422dd742" />


   iii) Now, this dataset is not in Brain Imaging Data Structure (BIDS) format (more information on BIDS here: https://bids.neuroimaging.io/); hence, uncheck the _BIDS_ check box on the right of the 'Participant Data Folder' text field. That will open a new window where the folder names can be entered. Type the following in the fields (as shown in the screenshot)

   a) Intermediate Folder --> session_1 
   
   (there is an intermediate folder between the participant data folder and the anatomical and functional file folder. If there is more than one folder, such as session_1 and then 'MRI' folder, one can put the path as session_1\MRI for Windows or session_1/MRI for Linux or Mac users)

   b) Functional Folder Name --> rest_1

   (the folder that contains the functional image)

   c) Anatomical Folder Name --> anat_1

   (the folder that contains the anatomical image)
   
   d) Functional Image Name --> rest

   (the .nii or .nii.gz functional image name; sometimes the participant name is there in the functional image name, then the common part can be mentioned and the participant name that changes for every participant can be replaced by a * . For instance, if the func file name is sub-1001.nii for participant 1001 and sub-1002.nii for participant 1002, one can put sub-*)
   
   e) Anatomical Image Name --> mprage

   (the .nii or .nii.gz anatomical image name; sometimes the participant name is there in the anatomical image name, then the common part can be mentioned and the participant name that changes for every participant can be replaced by a * . For instance, if the anat file name is sub-1001.nii for participant 1001 and sub-1002.nii for participant 1002, one can put sub-*)
         
![Screenshot 2025-03-13 164232](https://github.com/user-attachments/assets/4841cb8a-878e-48d6-87cc-41d8671b602a)

   f) Once all the fields are filled, click Submit. If the toolbox doesn't find a folder or file for the first participant, it will notify the folder or file not found, and changes can be made accordingly.

   iv) Next, check the 'All folders are participants' checkbox; this means we want to process every participant. Alternatively, one can just select a subset of participants if all participants should not be processed. This will display the number of participants that will be processed by WhiFuN (see screenshot below).
 
![Screenshot 2025-03-13 164504](https://github.com/user-attachments/assets/9b2f6ad0-be93-4130-a110-3399da96f157)

   v) Next, click on _Run Data Check_ and make sure that the functional and anatomical images are present for every participant and that all the MRI parameters of all the images are correct.

6) After the Data Check, a Data Check report will be shown. Make sure it says 'Data check completed successfully'.

7) Have a look at the preprocessing step parameters. If something needs to be changed, it can be changed (for more details, refer to the paper and manual).

8) Click _Run Preprocessing_.

9) Preprocessing will take some time, depending on the PC used. After preprocessing for one participant is done, WhiFuN will also display the estimated time to complete the preprocessing for all participants.

10) Once preprocessing is complete, please go to the output folder (using the file browser) and check the quality control plots saved for every participant (refer to the Quality Control section below or the paper/manual for more details).

11) Based on the quality control, participants with bad data should be excluded by checking the manually exclude participants checkbox in the _Construct FN and FC_ section. Once the participants are excluded, the White Matter Functional Networks (WM-FN) can be created (refer to the paper for more details on the parameters).

12) Click _Create WM-FN_, and WhiFuN will start creating the FN with the different values of K specified. After the cross-validation for every value of K specified is done, WhiFuN will plot the average dice coefficient and the distortion for every value of K (refer to the paper to find the optimal K value).

13) Choose the desired value of K and the WM-FN will be saved as a .nii file in `<outputs_folder>/Analysis/WM_FN`.

14) Similarly, GM-FN can be created.

15) Once the FNs are created, _Display_FN_ can be used to see the FNs using SPM or BrainNet Viewer (already included in the toolbox).

16) _Display_FC_ can be used to see the Functional Connectivity Matrix. If behavioral scores or age, sex csv file is also present, one can use the statistics module to fit a GLM and find the associations of behavioral data with the FC (more details in the paper).

## Using WhiFuN via Scripts (New in v3)

WhiFuN v3 introduces simplified scripting for automated batch processing. Two main approaches:

### Approach 1: Complete Pipeline Script

Use `whifun_preprocess_script_all.m` as a template for running the entire preprocessing pipeline without the GUI:

```matlab
% Set paths
whifun_path = 'path/to/WhiFuN';
spm_path = 'path/to/spm12';
data_path = 'path/to/participant/data';
output_folder = 'path/to/output';

% Configure data structure
app.comm_sess_name = 'session_1';
app.func_folder_name = 'rest_1';
app.anat_folder_name = 'anat_1';
app.func_data_name = 'rest';
app.anat_data_name = 'mprage';

% Set preprocessing parameters
n_vol_dis = 5;              % Discard first 5 volumes
max_fd = 6;                 % Motion thresholds
mean_fd = 0.25;
Reg_drop = 'Mean CSF';      % Regression type
smooth_drop = 'WM-GM Seperate';
smooth_fwhm = 4;
vox = 3;                    % MNI voxel size (mm)

% Run preprocessing (see whifun_preprocess_script_all.m for full example)
```

### Approach 2: Using Individual Functions

```matlab
% After initial data check, preprocess each participant:
Subj_list_1 = whifun_preproc(quality_control_path, Subj_list_1, ...
    'n_vol_dis', 5, ...
    'max_fd', 6, ...
    'mean_fd', 0.25, ...
    'Reg_CSF', 1, ...
    'motion_reg', 1, ...
    'smooth_fwhm', 4, ...
    'vox', 3);

% Create WM Functional Networks:
whifun_create_FN_Kmeans(output_folder, 'WM', 2, 22, group_mask_path, ...
    'CV_folds', 4, ...
    'over_write', 0);

% Create GM Functional Networks:
whifun_create_FN_Kmeans(output_folder, 'GM', 2, 22, group_mask_path, ...
    'CV_folds', 4);
```

See `whifun_preprocess_script_all.m` and `Create_WM_FN_script.m` for complete examples.

## Using WhiFuN with Externally Preprocessed Data (New in v3)

WhiFuN v3 can work with data preprocessed by other pipelines (fMRIPrep, CONN, DPARSF, etc.).

To use WhiFuN for network creation on externally preprocessed data:

```matlab
% Launch the function (with or without output folder)
whifun_using_other_preproc(output_folder)

% Or let it prompt you for the output folder:
whifun_using_other_preproc()
```

This function will:
1. Guide you through creating a participant list linking to your preprocessed files
2. Perform a data check to verify file integrity
3. Generate quality control plots on your preprocessed data
4. Create an output folder structure compatible with the WhiFuN GUI

After running this function, you can load the output folder in the WhiFuN GUI to create WM and GM Functional Networks using your externally preprocessed data.

**Requirements for external data:**
- Functional images must be in MNI space (NIfTI format)
- Anatomical T1 images (optional, for better QC visualization)
- Tissue segmentation maps (GM, WM, CSF) if available

## DARTEL Normalization (New in v3)

WhiFuN v3 includes DARTEL-based registration for improved anatomical alignment:

**When to use DARTEL:**
- When you need more accurate inter-participant registration
- For studies requiring precise anatomical correspondence
- When standard normalization shows poor alignment

**How to use:**
1. During preprocessing, select "DARTEL" from the normalization dropdown in the GUI
2. Or in scripts, use the `whifun_dartel.m` and `whifun_dartel_normalize_smooth.m` functions
3. DARTEL creates a group template from all participants, then normalizes each participant to this template

**Note:** DARTEL increases preprocessing time significantly (several hours for large datasets) but provides superior registration quality.

## Quality Control Reports (Enhanced in v3)

After preprocessing, thoroughly review the Quality Control plots in the output folder. WhiFuN v3 generates comprehensive QC reports organized in folders:

**a_Initial_check:** Shows initial alignment of anatomical and functional images relative to MNI space. Check for flipped or incorrectly oriented images.

**b_Head_motion:** Contains framewise displacement (FD) plots, translational and rotational motion plots. Participants exceeding motion thresholds are automatically flagged. Includes:
- Framewise displacement time series
- Summary of motion parameters
- List of excluded participants

**c_Segmentation:** Displays Gray Matter (red), White Matter (green), and CSF (blue) overlaid on the anatomical image. Verify that tissue types are correctly identified.

**d_Co_registeration:** Shows functional-to-anatomical alignment with contour overlays. Ensure proper registration between modalities.

**e_CSF_Masks_for_Regression:** (if nuisance regression enabled) Verifies CSF mask alignment with functional data.

**f_Nuisance_Regression:** Mean time series before and after regression, showing the effect of noise removal.

**g_Filtering:** (if filtering enabled) Frequency response plots showing the effect of temporal filtering.

**h_Smoothing:** Displays spatially smoothed functional images.

**i_Final_func_MNI:** Final preprocessed functional images in MNI space overlaid on the MNI template.

**j_Time_series_check:** Comprehensive time series QC showing:
- (A) Global mean intensity for raw fMRI
- (B) Six rigid-body motion parameters
- (C) Task design regressors (if applicable)
- (D) Correlations among A-C
- (E) Variance between consecutive images
- (F) Framewise displacement
- (G) Derivatives of regressors
- (H) Correlations among E-G

**k_Seed_Based_Corr (NEW in v3):** Seed-based correlation maps for three major networks:
- **Default Mode Network:** Posterior Cingulate Cortex seed (5, -49, 40)
- **Visual Network:** Visual cortex seed (-4, -91, -3)
- **Auditory Network:** Auditory cortex seed (64, -12, 2)

These maps help identify participants with poor functional connectivity patterns or excessive noise. A well-preprocessed dataset should show clear, expected network patterns.

**Error_Info.txt:** If preprocessing errors occur for any participant, details are logged here with timestamps, error messages, and line numbers for debugging.

## Troubleshooting

**"SPM path not set" error:**
- Ensure SPM12 is added to MATLAB path before running WhiFuN
- Use: `addpath('path/to/spm12')` or the Set Path GUI

**Memory issues during network creation:**
- Increase voxel size (use 3mm or 4mm instead of 2mm)
- Reduce the number of participants
- Enable chunking (already default in v3)

**Motion artifacts:**
- Adjust FD thresholds if too many/few participants are rejected
- Review motion plots in Quality Control folder
- Consider more stringent motion correction

**Poor segmentation:**
- Check anatomical image quality
- Try adjusting CSF threshold parameter
- Use DARTEL for better registration

**External preprocessing data not working:**
- Ensure functional images are in MNI space
- Check file naming consistency
- Verify NIfTI format compatibility

For additional help, open an issue on GitHub or email: jainpratik412[at]gmail[dot]com

## Additional Resources

Refer to the WhiFuN Manual (WhiFuN-Manual.pdf included in the toolbox) for detailed documentation and understanding all features of WhiFuN.

**For detailed help on any function:**
```matlab
>> help whifun_preproc               % Preprocessing pipeline
>> help whifun_create_FN_Kmeans      % Create WM/GM networks
>> help whifun_using_other_preproc   % Use external preprocessing
>> help whifun_check_data            % Initial data verification
```
