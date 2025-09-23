import os
import logging
import numpy as np

from pywhifun.utils.io import load_subjects_from_csv, write_list_of_dicts_to_csv, unzip_nifti_if_needed
from pywhifun.utils.logging import setup_file_logger, log_error_to_file
from pywhifun.preprocessing.motion import calculate_fd_sum

# Configure basic logging for console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This file will contain the high-level logic for the preprocessing pipeline.
# For now, it is composed of stub functions that log what they *would* do.

# --- Stub Functions ---
# These will eventually be replaced by calls to the real, converted functions
# from other modules (e.g., pywhifun.preprocessing.motion).

def _discard_volumes_stub(func_path, n_vols):
    if n_vols > 0:
        logging.info(f"PIPELINE STUB: Discarding {n_vols} volumes from {func_path}")
        new_func_path = func_path.replace('.nii', '_trimmed.nii')
        logging.info(f"PIPELINE STUB: --> Would create {new_func_path}")
        return new_func_path
    logging.info("PIPELINE STUB: Skipping volume discarding (n_vol_dis = 0).")
    return func_path

def _realign_stub(func_path):
    logging.info(f"PIPELINE STUB: Realigning (motion correcting) {func_path}")
    realigned_path = func_path.replace('.nii', '_realigned.nii')
    motion_params_path = func_path.replace('.nii', '_motion.txt')
    logging.info(f"PIPELINE STUB: --> Would create {realigned_path} and {motion_params_path}")
    return realigned_path, motion_params_path


def _segment_stub(anat_path):
    logging.info(f"PIPELINE STUB: Segmenting {anat_path} into tissue types.")
    return "/path/to/c1anat.nii", "/path/to/c2anat.nii"

def _skullstrip_stub(anat_path, segmentation_files):
    logging.info(f"PIPELINE STUB: Skull-stripping {anat_path}")
    return "/path/to/brain_anat.nii"

def _coregister_stub(anat_path, func_path):
    logging.info(f"PIPELINE STUB: Coregistering {anat_path} to {func_path}")
    return True # Success

def _regression_stub(func_path, anat_path, params):
    logging.info(f"PIPELINE STUB: Performing nuisance signal regression on {func_path}")
    regressed_path = func_path.replace('.nii', '_regressed.nii')
    logging.info(f"PIPELINE STUB: --> Would create {regressed_path}")
    return regressed_path

def _filter_stub(func_path, params):
    logging.info(f"PIPELINE STUB: Applying temporal filter to {func_path}")
    filtered_path = func_path.replace('.nii', '_filtered.nii')
    logging.info(f"PIPELINE STUB: --> Would create {filtered_path}")
    return filtered_path

def _smooth_stub(func_path, params):
    logging.info(f"PIPELINE STUB: Applying spatial smoothing to {func_path}")
    smoothed_path = func_path.replace('.nii', '_smoothed.nii')
    logging.info(f"PIPELINE STUB: --> Would create {smoothed_path}")
    return smoothed_path

def _normalize_stub(func_path, anat_path, params):
    logging.info(f"PIPELINE STUB: Normalizing {func_path} to MNI space.")
    normalized_path = func_path.replace('.nii', '_normalized.nii')
    logging.info(f"PIPELINE STUB: --> Would create {normalized_path}")
    return normalized_path

# --- Main Pipeline Function ---

def run_preprocessing_pipeline(output_folder: str, subject_list_csv: str, params: dict):
    """
    Runs the full (stubbed) fMRI preprocessing pipeline.

    This function orchestrates the sequence of preprocessing steps for each subject.
    Currently, most steps are implemented as stubs that log their actions.

    Args:
        output_folder (str): Path to the main output directory.
        subject_list_csv (str): Name of the CSV file containing subject info.
        params (dict): A dictionary of preprocessing parameters.
    """
    logging.info("--- Starting PyWhiFuN Preprocessing Pipeline ---")

    # --- Setup: Error Logging and Parameters ---
    error_log_path = os.path.join(output_folder, 'pywhifun_error_log.txt')
    error_logger = setup_file_logger('error_logger', error_log_path)
    logging.info(f"Error log will be saved to: {error_log_path}")

    # --- Step 1: Load Subjects (REAL IMPLEMENTATION) ---
    subject_csv_path = os.path.join(output_folder, subject_list_csv)
    all_subjects = load_subjects_from_csv(subject_csv_path, filter_subjects=False)
    subjects_to_process = [s for s in all_subjects if not s.get('error') and not s.get('motion_ex') and not s.get('manual_ex')]

    if not subjects_to_process:
        logging.error(f"No valid subjects found in {subject_csv_path} or file not found. Aborting pipeline.")
        return False

    logging.info(f"Found {len(subjects_to_process)} valid subjects to process out of {len(all_subjects)} total.")

    for i, subject in enumerate(all_subjects):
        # Skip subjects that are already marked for exclusion
        if subject not in subjects_to_process:
            continue

        logging.info(f"--- Processing Subject: {subject['name']} ---")
        try:
            # --- Step 2: Unzip Files (REAL IMPLEMENTATION) ---
            # This logic is simple enough to live here for now.
            # In MATLAB, this is mixed with finding the file. We assume paths are correct.
            logging.info("PIPELINE: Checking/Unzipping files...")
            subject['func_file'] = unzip_nifti_if_needed(subject['func_file_path'])
            subject['anat_file'] = unzip_nifti_if_needed(subject['anat_file_path'])

            # --- Step 3: Discard Initial Volumes ---
            trimmed_file = _discard_volumes_stub(subject['func_file'], params.get('n_vol_dis', 0))

            # --- Step 4: Realignment ---
            realigned_file, motion_params_path = _realign_stub(trimmed_file)

            # --- Step 5: Framewise Displacement Check (REAL IMPLEMENTATION) ---
            logging.info("PIPELINE: Calculating FD and checking against thresholds.")
            motion_params = np.loadtxt(motion_params_path) # In reality, we'd load the file
            fd = calculate_fd_sum(motion_params)

            if np.max(fd) > params.get('max_fd', 6):
                logging.warning(f"Excluding subject {subject['name']} due to max FD > threshold.")
                all_subjects[i]['motion_ex'] = 1
                continue
            # (Add other FD checks here: mean_fd, etc.)

            # --- Step 6: Segmentation ---
            c1_file, c2_file = _segment_stub(subject['anat_file'])


            # --- Step 7: Skull Stripping ---
            skullstripped_anat = _skullstrip_stub(subject['anat_file'], [c1_file, c2_file])

            # --- Step 8: Coregistration ---
            _coregister_stub(skullstripped_anat, realigned_file)

            # The order of the next steps depends on the parameters
            processed_file = realigned_file
            if params.get('Reg_', 1): # Default is to regress
                processed_file = _regression_stub(processed_file, skullstripped_anat, params)

            if params.get('filter_check', 0):
                processed_file = _filter_stub(processed_file, params)

            if params.get('Smooth_', 1): # Default is to smooth
                processed_file = _smooth_stub(processed_file, params)

            # --- Step 14: Normalization ---
            final_file = _normalize_stub(processed_file, subject['anat_file'], params)

            logging.info(f"--- Subject {subject['name']} processed successfully. Final file: {final_file} ---")

        except Exception as e:
            logging.error(f"PIPELINE ERROR: Failed to process subject {subject['name']}.")
            log_error_to_file(error_logger, subject['name'], e)
            all_subjects[i]['error'] = 1

    # --- Final Step: Save Updated Subject List (REAL IMPLEMENTATION) ---
    logging.info("--- PyWhiFuN Preprocessing Pipeline Finished ---")
    logging.info("Saving updated subject list to CSV.")
    write_list_of_dicts_to_csv(all_subjects, subject_csv_path)

    return True
