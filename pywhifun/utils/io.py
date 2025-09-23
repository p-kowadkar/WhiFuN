import numpy as np
import nibabel as nib
from numpy.typing import ArrayLike
from typing import Optional

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
