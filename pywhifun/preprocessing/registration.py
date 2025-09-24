import logging
from typing import List, Optional

def coregister_image_stub(
    reference_path: str,
    source_path: str,
    other_paths: Optional[List[str]] = None
) -> bool:
    """
    A placeholder stub for the coregistration step.

    WARNING: This function does not perform any actual coregistration.
    It is a placeholder to allow the pipeline to run end-to-end. It does
    not modify any files.

    Args:
        reference_path (str): Path to the reference image (e.g., anatomical).
        source_path (str): Path to the source image to be aligned (e.g., mean fMRI).
        other_paths (list, optional): List of other images to apply the same
                                      transformation to. Defaults to None.

    Returns:
        bool: Always returns True to indicate "success".
    """
    logging.warning("COREGISTRATION STEP IS A STUB. No alignment is being performed.")
    logging.info(f"STUB: Would align {source_path} to {reference_path}.")
    if other_paths:
        logging.info(f"STUB: Would apply the same transform to {len(other_paths)} other images.")

    return True