import logging

def normalize_image_stub(func_path: str, anat_path: str, params: dict) -> str:
    """
    A placeholder stub for the spatial normalization step.

    Args:
        func_path (str): Path to the functional image.
        anat_path (str): Path to the anatomical image.
        params (dict): Dictionary of parameters.

    Returns:
        str: Path to the dummy output file.
    """
    logging.warning("NORMALIZATION STEP IS A STUB. No normalization is being performed.")
    return func_path.replace('.nii', '_normalized.nii')