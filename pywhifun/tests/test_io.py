import numpy as np
import nibabel as nib
import pytest
from numpy.testing import assert_allclose
from pywhifun.utils.io import save_nifti

@pytest.fixture
def template_nifti_image():
    """Creates a dummy template NIfTI image for testing."""
    # Using a non-identity affine to make the test more robust
    affine = np.array([
        [-2., 0., 0., 100.],
        [0., -2., 0., 100.],
        [0., 0., 2., -50.],
        [0., 0., 0., 1.]
    ])
    # The template data itself doesn't matter, just its shape and type
    template_data = np.zeros((10, 10, 10), dtype=np.float64)
    template_img = nib.Nifti1Image(template_data, affine)
    return template_img

def test_save_nifti_basic(template_nifti_image, tmp_path):
    """Tests basic saving and loading of a NIfTI file."""
    output_filename = tmp_path / "test_output.nii.gz"

    # The new data we want to save
    new_data = np.arange(64, dtype=np.int16).reshape((4, 4, 4))

    save_nifti(new_data, str(output_filename), template_nifti_image)

    # Load the file back and verify its contents
    assert output_filename.exists()
    loaded_img = nib.load(output_filename)

    # 1. Check that the data was saved correctly
    assert_allclose(loaded_img.get_fdata(), new_data)

    # 2. Check that the affine was copied from the template
    assert_allclose(loaded_img.affine, template_nifti_image.affine)

    # 3. Check that the datatype in the header was updated correctly
    assert loaded_img.get_data_dtype() == np.int16

# def test_save_nifti_header_updates(tmp_path):
#     """
#     TODO: This test is disabled as there is a persistent bug with saving
#     scl_slope and scl_inter header fields using nibabel. The value is not
#     written to disk correctly. This needs to be revisited.
#     """
#     output_filename = tmp_path / "scratch_test.nii.gz"
#
#     # 1. Create data and affine
#     data = np.arange(8, dtype=np.int16).reshape((2, 2, 2))
#     affine = np.diag([-2, 2, 3, 1])
#
#     # 2. Create the image object
#     img = nib.Nifti1Image(data, affine)
#
#     # 3. Explicitly set the data type in the header. This is a critical step.
#     # The header needs to know the on-disk format will be integer.
#     img.set_data_dtype(np.int16)
#
#     # 4. Set the scaling factors.
#     img.header.set_slope_inter(slope=2.5, inter=-1.0)
#
#     # 5. Save the image
#     nib.save(img, str(output_filename))
#
#     # 6. Load back and verify
#     loaded_img = nib.load(output_filename)
#
#     assert loaded_img.header['scl_slope'] == 2.5
#     assert loaded_img.header['scl_inter'] == -1.0
#
#     # Also check that get_fdata() applies the scaling correctly
#     expected_fdata = data * 2.5 - 1.0
#     assert_allclose(loaded_img.get_fdata(), expected_fdata)
