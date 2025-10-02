import os
import logging
import numpy as np

# --- Import all pipeline steps from their respective modules ---
# Real implementations that can be used now
from pywhifun.utils.io import load_subjects_from_csv, write_list_of_dicts_to_csv, unzip_nifti_if_needed
from pywhifun.utils.logging import setup_file_logger, log_error_to_file

# Stubs for blocked/unimplemented steps
from pywhifun.preprocessing.motion import realign_image_stub, fd_check_stub
from pywhifun.preprocessing.masking import skullstrip_stub, create_csf_mask_stub
from pywhifun.preprocessing.segmentation import segment_image_stub
from pywhifun.preprocessing.registration import coregister_image_stub
from pywhifun.preprocessing.regression import nuisance_regression_stub
from pywhifun.preprocessing.filtering import temporal_filter_stub
from pywhifun.preprocessing.smoothing import spatial_smooth_stub
from pywhifun.preprocessing.normalization import normalize_image_stub

# Configure basic logging for console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_preprocessing_pipeline(output_folder: str, subject_list_csv: str, params: dict, progress_callback=None):
    """
    Runs the fMRI preprocessing pipeline by calling a sequence of modules.
    """
    logging.info("--- Starting PyWhiFuN Preprocessing Pipeline ---")

    error_log_path = os.path.join(output_folder, 'pywhifun_error_log.txt')
    error_logger = setup_file_logger('error_logger', error_log_path)
    logging.info(f"Error log will be saved to: {error_log_path}")

    subject_csv_path = os.path.join(output_folder, subject_list_csv)
    all_subjects = load_subjects_from_csv(subject_csv_path, filter_subjects=False)
    subjects_to_process = [s for s in all_subjects if not (s.get('error') or s.get('motion_ex') or s.get('manual_ex'))]

    if not subjects_to_process:
        logging.error(f"No valid subjects found in {subject_csv_path} or file not found. Aborting pipeline.")
        return False

    logging.info(f"Found {len(subjects_to_process)} valid subjects to process out of {len(all_subjects)} total.")

    num_subjects = len(subjects_to_process)
    for i, subject in enumerate(subjects_to_process):
        # This is a bit inefficient, but ensures we update the correct subject
        # in the main list if they are excluded.
        subject_index_in_full_list = [idx for idx, d in enumerate(all_subjects) if d['name'] == subject['name']][0]

        if progress_callback:
            progress = int((i / num_subjects) * 100)
            progress_callback(progress)

        logging.info(f"--- Processing Subject: {subject['name']} ({i+1}/{num_subjects}) ---")
        try:
            # This assumes the CSV contains 'func_file_path' and 'anat_file_path' columns
            subject['func_file'] = unzip_nifti_if_needed(subject.get('func_file_path', ''))
            subject['anat_file'] = unzip_nifti_if_needed(subject.get('anat_file_path', ''))

            # --- The Pipeline ---
            realigned_file, motion_params_path = realign_image_stub(subject['func_file'], params.get('Realign_pre', 'r'))

            is_excluded = fd_check_stub(motion_params_path, subject, params)
            if is_excluded:
                all_subjects[subject_index_in_full_list]['motion_ex'] = 1
                continue

            segmentation_files = segment_image_stub(subject['anat_file'])

            skullstripped_anat_path = skullstrip_stub(subject['anat_file'], segmentation_files)

            coregister_image_stub(skullstripped_anat_path, realigned_file)

            processed_file = realigned_file
            if params.get('Reg_', 1):
                csf_mask_path = create_csf_mask_stub(subject['anat_file'], segmentation_files, params)
                processed_file = nuisance_regression_stub(processed_file, skullstripped_anat_path, params)

            if params.get('filter_check', 0):
                processed_file = temporal_filter_stub(processed_file, params)

            if params.get('Smooth_', 1):
                processed_file = spatial_smooth_stub(processed_file, params)

            final_file = normalize_image_stub(processed_file, subject['anat_file'], params)

            logging.info(f"--- Subject {subject['name']} processed successfully. Final file: {final_file} ---")

        except Exception as e:
            logging.error(f"PIPELINE ERROR: Failed to process subject {subject['name']}.")
            log_error_to_file(error_logger, subject['name'], e)
            all_subjects[subject_index_in_full_list]['error'] = 1

    logging.info("--- PyWhiFuN Preprocessing Pipeline Finished ---")
    write_list_of_dicts_to_csv(all_subjects, subject_csv_path)

    if progress_callback:
        progress_callback(100)
    return True