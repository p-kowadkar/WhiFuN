import numpy as np
import nibabel as nib
from pywhifun.utils.io import save_nifti
import logging

def skullstrip_image(
    anat_path: str,
    gm_path: str,
    wm_path: str,
    csf_path: str,
    output_path: str,
    threshold: float = 0.5
) -> bool:
    """
    Creates a skull-stripped image by masking with tissue probability maps.

    This function replicates the logic of `whifun_skullstrip.m`, which uses
    SPM's imcalc to create a brain mask from Gray Matter (GM), White Matter (WM),
    and CSF tissue probability maps and applies it to the anatomical image.

    Args:
        anat_path (str): Path to the anatomical image to be skull-stripped.
        gm_path (str): Path to the Gray Matter probability map (c1).
        wm_path (str): Path to the White Matter probability map (c2).
        csf_path (str): Path to the CSF probability map (c3).
        output_path (str): Path to save the skull-stripped output NIfTI file.
        threshold (float): Combined probability threshold to create the brain
                           mask. Defaults to 0.5.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Load all the required images
        logging.info(f"Loading anatomical image: {anat_path}")
        anat_img = nib.load(anat_path)
        anat_data = anat_img.get_fdata()

        logging.info(f"Loading GM, WM, and CSF maps: {gm_path}, {wm_path}, {csf_path}")
        gm_data = nib.load(gm_path).get_fdata()
        wm_data = nib.load(wm_path).get_fdata()
        csf_data = nib.load(csf_path).get_fdata()

        # Create the brain mask by summing probabilities and thresholding
        logging.info(f"Creating brain mask with threshold > {threshold}")
        brain_mask = (gm_data + wm_data + csf_data) > threshold

        # Apply the mask to the anatomical data (element-wise multiplication)
        skullstripped_data = anat_data * brain_mask

        # Save the new skull-stripped image using the original as a template
        logging.info(f"Saving skull-stripped image to: {output_path}")
        save_nifti(skullstripped_data.astype(anat_img.get_data_dtype()), output_path, anat_img)

        return True

    except Exception as e:
        logging.error(f"Error during skull-stripping: {e}", exc_info=True)
        return False


def create_csf_mask(
    csf_tpm_path: str,
    ref_img_path: str,
    output_path: str,
    threshold: float
) -> bool:
    """
    Creates a binary CSF mask by thresholding a probability map.

    This function replicates the logic of `whifun_create_csf_mask.m`.

    Args:
        csf_tpm_path (str): Path to the CSF tissue probability map (TPM).
        ref_img_path (str): Path to a reference image (e.g., a functional image)
                            to use for header and affine information.
        output_path (str): Path to save the output binary mask NIfTI file.
        threshold (float): Probability threshold to apply to the TPM.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        logging.info(f"Loading CSF TPM: {csf_tpm_path}")
        csf_img = nib.load(csf_tpm_path)
        csf_data = csf_img.get_fdata()

        logging.info(f"Loading reference image for geometry: {ref_img_path}")
        ref_img = nib.load(ref_img_path)

        logging.info(f"Thresholding CSF map at > {threshold}")
        # Create binary mask and ensure it has an integer type
        csf_mask = (csf_data > threshold).astype(np.int16)

        # Save the new mask using the reference image as a template
        logging.info(f"Saving CSF mask to: {output_path}")
        save_nifti(csf_mask, output_path, ref_img)

        return True

    except Exception as e:
        logging.error(f"Error during CSF mask creation: {e}", exc_info=True)
        return False