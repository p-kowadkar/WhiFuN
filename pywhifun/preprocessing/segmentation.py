import os
import logging
import numpy as np
import nibabel as nib
from pywhifun.utils.io import save_nifti

def segment_image_stub(anat_path: str) -> dict:
    """
    A placeholder stub for the segmentation and normalization step.

    WARNING: This function does not perform any actual segmentation.
    It creates empty dummy files for the expected outputs of SPM's
    segmentation routine to allow the pipeline to continue.

    Args:
        anat_path (str): The path to the input anatomical NIfTI file.

    Returns:
        A dictionary containing paths to the created dummy files, e.g.,
        {'gm': '/path/to/c1anat.nii', 'fwd_def': '/path/to/y_anat.nii', ...}
    """
    logging.warning("SEGMENTATION STEP IS A STUB. No tissue segmentation is being performed.")

    dirname, filename = os.path.split(anat_path)

    # Load the original anatomical image to use as a template for dummy files
    try:
        template_img = nib.load(anat_path)
        dummy_data = np.zeros(template_img.shape, dtype=np.float32)
    except Exception as e:
        logging.error(f"Could not load template anat file {anat_path}: {e}")
        # Create a default template if loading fails to prevent crashing
        template_img = nib.Nifti1Image(np.zeros((10,10,10)), np.eye(4))
        dummy_data = np.zeros((10,10,10), dtype=np.float32)

    output_files = {}
    # Prefixes for Gray Matter, White Matter, CSF, and deformation fields
    prefixes = {
        'gm': 'c1',
        'wm': 'c2',
        'csf': 'c3',
        'fwd_def': 'y_',
        'inv_def': 'iy_'
    }

    for key, prefix in prefixes.items():
        # SPM prepends to the original filename
        output_filename = os.path.join(dirname, f"{prefix}{filename}")
        # The save_nifti function is currently bugged for some headers, but should
        # work for creating simple empty files.
        save_nifti(dummy_data, output_filename, template_img)
        output_files[key] = output_filename
        logging.info(f"STUB: Created dummy file at {output_filename}")

    return output_files
