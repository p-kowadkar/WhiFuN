import os
import gzip
import shutil
import numpy as np
import nibabel as nib
import pandas as pd
from numpy.typing import ArrayLike
from typing import Optional, List, Dict, Any


def save_nifti(data: ArrayLike, filename: str, template_img: nib.Nifti1Image, **header_updates):
    """
    Saves a data array as a NIfTI file, using another NIfTI image as a template.

    This function replicates the logic of `niftisave.m` from WhiFuN. It takes
    a data array and a template nibabel image object, and saves a new NIfTI
    file with the new data but the affine and header from the template,
    with some fields updated to match the new data.

    Args:
        data (ArrayLike): The numpy data array to be saved.
        filename (str): The path to save the new NIfTI file to.
        template_img (nib.Nifti1Image): A nibabel image object to use as a
                                       template for the affine and header.
        **header_updates: Optional keyword arguments to update specific fields
                          in the header of the new NIfTI image.
                          e.g., scl_slope=1.0, scl_inter=0.0
    """
    data = np.asarray(data)

    # Create a copy of the header from the template to modify. This is safer.
    new_header = template_img.header.copy()

    # Set the data type for the new data on the header.
    new_header.set_data_dtype(data.dtype)

    # Set slope and intercept on the new header *before* creating the image object.
    # This appears to be crucial for ensuring nibabel respects these fields.
    slope = header_updates.get('scl_slope')
    inter = header_updates.get('scl_inter')
    if slope is not None or inter is not None:
        new_header.set_slope_inter(slope, inter)

    # Create the new NIfTI image object using the fully prepared header
    # and the template's affine.
    new_img = nib.Nifti1Image(data, template_img.affine, new_header)

    # Save the new image to the specified file.
    nib.save(new_img, filename)


def load_subjects_from_csv(
    filepath: str,
    filter_subjects: bool = True
) -> List[Dict[str, Any]]:
    """
    Loads a subject list from a CSV file and optionally filters it.

    This function replicates the logic of `load_subjects` and `load_subjects_all`
    from the WhiFuN MATLAB scripts by consolidating them.

    Args:
        filepath (str): The full path to the subject CSV file.
        filter_subjects (bool): If True, excludes subjects based on the
                                'error', 'motion_ex', and 'manual_ex' columns.
                                If False, loads all subjects. Defaults to True.

    Returns:
        A list of dictionaries, where each dictionary represents a subject
        and contains the information from one row of the CSV.
        Returns an empty list if the file cannot be read.
    """
    try:
        # Ensure the 'name' column is read as a string, even if it's all numbers
        df = pd.read_csv(filepath, dtype={'name': str})
    except FileNotFoundError:
        # In a real library, a logger would be better than print.
        print(f"Warning: Subject CSV not found at {filepath}")
        return []

    if not filter_subjects:
        return df.to_dict(orient='records')

    # Build an exclusion mask based on any of the exclusion columns being true (1)
    exclusion_mask = pd.Series(False, index=df.index)
    for col in ['error', 'motion_ex', 'manual_ex']:
        if col in df.columns:
            # The | operator performs a logical OR
            exclusion_mask = exclusion_mask | (df[col] == 1)

    df_filtered = df[~exclusion_mask]

    return df_filtered.to_dict(orient='records')


def write_list_of_dicts_to_csv(data: List[Dict[str, Any]], filepath: str) -> bool:
    """
    Converts a list of dictionaries to a pandas DataFrame and saves it to CSV.

    This function is a Python equivalent of the `my_writetable` logic used
    in the WhiFuN MATLAB scripts.

    Args:
        data (List[Dict[str, Any]]): The data to be saved, where each dict is a row.
        filepath (str): The full path to the output CSV file.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    if not isinstance(data, list) or not data:
        # In a real library, a logger would be better than print.
        print("Warning: Input data is empty or not a list. Nothing to write to CSV.")
        return False
    try:
        df = pd.DataFrame.from_records(data)
        df.to_csv(filepath, index=False)
        return True
    except Exception as e:
        print(f"Error writing to CSV file {filepath}: {e}")
        return False


def unzip_nifti_if_needed(filepath: str) -> str:
    """
    Decompresses a .nii.gz file to a .nii file if not already done.

    Checks for a .nii.gz file and decompresses it to the same location
    without the .gz extension, but only if the .nii file does not
    already exist.

    Args:
        filepath (str): The path to the NIfTI file (can be .nii or .nii.gz).

    Returns:
        str: The path to the (potentially unzipped) .nii file. If the input
             was not a .gz file, it returns the original path.
    """
    if filepath.endswith(".nii.gz"):
        unzipped_path = filepath[:-3]  # Remove .gz
        if not os.path.exists(unzipped_path):
            try:
                with gzip.open(filepath, 'rb') as f_in:
                    with open(unzipped_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return unzipped_path
            except FileNotFoundError:
                # In a real library, a logger would be better than print.
                print(f"Warning: Source file not found for unzipping: {filepath}")
                return filepath  # Return original path if source not found
        else:
            # The unzipped file already exists
            return unzipped_path
    else:
        # Not a gzipped file, return original path
        return filepath
