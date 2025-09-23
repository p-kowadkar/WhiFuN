import os
import shutil
import logging
import numpy as np
import nibabel as nib
from numpy.typing import ArrayLike

def calculate_fd(motion_params: ArrayLike) -> np.ndarray:
    """
    Calculates Framewise Displacement (FD).

    This function replicates the specific FD calculation from `fd_calc.m`
    in the WhiFuN toolbox, which is the Euclidean norm (L2 norm) of the
    temporal difference of the motion parameters.

    Note: This is a simplified FD calculation and may differ from other
    implementations (e.g., Power et al., 2012) which apply a
    transformation to rotational parameters before calculating displacement.

    Args:
        motion_params: A 2D numpy array of shape (n_timepoints, n_params)
                       containing the motion parameters (e.g., 3 translations
                       and 3 rotations).

    Returns:
        A 1D numpy array of shape (n_timepoints - 1,) containing the
        Framewise Displacement for each time point.

    Raises:
        ValueError: If the input array is not 2D or has fewer than 2 timepoints.
    """
    motion_params = np.asarray(motion_params)

    if motion_params.ndim != 2 or motion_params.shape[0] < 2:
        raise ValueError("motion_params must be a 2D array with at least 2 timepoints.")

    # Calculate temporal difference (row-wise)
    diff_matrix = np.diff(motion_params, axis=0)

    # Calculate the L2 norm of each row of the difference matrix
    fd = np.linalg.norm(diff_matrix, axis=1)

    return fd


def calculate_fd_sum(motion_params: ArrayLike, rot_radius: float = 50.0) -> np.ndarray:
    """
    Calculates Framewise Displacement (FD) using a sum of differences.

    This function replicates the specific FD calculation found inside the main
    `whifun_preprocess_script.m` script. It is a non-standard method where
    the raw differences (not absolute values) are summed.

    The formula is:
    fd(t) = sum(diff(translations)) + sum(diff(rotations) * radius)

    Args:
        motion_params (ArrayLike): A 2D numpy array of shape (n_timepoints, 6)
                                   containing 3 translation and 3 rotation
                                   parameters.
        rot_radius (float): The radius (in mm) used to convert rotational
                            parameters to displacements. Defaults to 50.0.

    Returns:
        np.ndarray: A 1D numpy array of shape (n_timepoints - 1,) containing
                    the FD values.
    """
    motion_params = np.asarray(motion_params)

    if motion_params.ndim != 2 or motion_params.shape[0] < 2 or motion_params.shape[1] != 6:
        raise ValueError("motion_params must be a 2D array of shape (n_timepoints, 6).")

    # Calculate temporal difference
    diff_matrix = np.diff(motion_params, axis=0)

    # Separate translation and rotation
    trans_diff = diff_matrix[:, :3]
    rot_diff = diff_matrix[:, 3:]

    # Scale rotation and calculate FD as per the script's formula
    fd = np.sum(trans_diff, axis=1) + np.sum(rot_diff * rot_radius, axis=1)

    return fd


def realign_image_stub(nifti_path: str, output_prefix: str = 'r') -> (str, str):
    """
    A placeholder stub for the realignment (motion correction) step.

    WARNING: This function does not perform any actual realignment.
    It is a placeholder to allow the pipeline to run end-to-end.

    It copies the input file to a new file with the specified prefix and
    creates a dummy motion parameter file filled with zeros.

    Args:
        nifti_path (str): The path to the input 4D NIfTI file.
        output_prefix (str): The prefix to add to the output filename.

    Returns:
        A tuple containing:
        - realigned_path (str): Path to the "realigned" (copied) file.
        - motion_params_path (str): Path to the dummy motion parameter file.
    """
    logging.warning("REALIGNMENT STEP IS A STUB. No motion correction is being performed.")

    # Construct output paths
    dirname, filename = os.path.split(nifti_path)
    realigned_path = os.path.join(dirname, f"{output_prefix}{filename}")

    # Create the motion parameter filename (e.g., rp_c_sub-01.txt)
    # This needs to match the naming convention from the MATLAB script
    base_name = filename.split('.')[0] # e.g., c_sub-01_task-rest_bold
    motion_params_filename = f"rp_{base_name}.txt"
    motion_params_path = os.path.join(dirname, motion_params_filename)

    # 1. Copy the original file to the new "realigned" location
    shutil.copyfile(nifti_path, realigned_path)
    logging.info(f"STUB: Copied {nifti_path} to {realigned_path}")

    # 2. Create a dummy motion parameter file with zeros
    # We need to know the number of timepoints. We can load the image for this.
    try:
        img = nib.load(nifti_path)
        n_timepoints = img.shape[3] if len(img.shape) > 3 else 1
    except Exception:
        n_timepoints = 180 # A reasonable default if loading fails
        logging.warning(f"Could not load {nifti_path} to get timepoints. Creating dummy motion file with {n_timepoints} rows.")

    dummy_motion_params = np.zeros((n_timepoints, 6))
    np.savetxt(motion_params_path, dummy_motion_params, fmt='%.6f')
    logging.info(f"STUB: Created dummy motion file at {motion_params_path}")

    return realigned_path, motion_params_path
