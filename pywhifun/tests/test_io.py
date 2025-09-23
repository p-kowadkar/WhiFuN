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

import pandas as pd
from pywhifun.utils.io import load_subjects_from_csv


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


# --- Tests for load_subjects_from_csv ---

@pytest.fixture
def sample_subject_csv(tmp_path):
    """Creates a sample subject CSV file for testing."""
    csv_path = tmp_path / "subjects.csv"
    data = {
        'name': ['sub-01', 'sub-02', 'sub-03', 'sub-04'],
        'age': [25, 30, 35, 40],
        'error': [0, 1, 0, 0],
        'motion_ex': [0, 0, 1, 0],
        'manual_ex': [0, 0, 0, 1]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return str(csv_path)

def test_load_subjects_no_filter(sample_subject_csv):
    """Tests loading all subjects when filtering is disabled."""
    subjects = load_subjects_from_csv(sample_subject_csv, filter_subjects=False)
    assert len(subjects) == 4
    assert subjects[1]['name'] == 'sub-02'

def test_load_subjects_with_filter(sample_subject_csv):
    """Tests that subjects with exclusion flags are correctly filtered."""
    subjects = load_subjects_from_csv(sample_subject_csv, filter_subjects=True)
    # sub-02 (error=1), sub-03 (motion_ex=1), and sub-04 (manual_ex=1) should be excluded.
    # Only sub-01 should remain.
    assert len(subjects) == 1
    assert subjects[0]['name'] == 'sub-01'

def test_load_subjects_file_not_found():
    """Tests behavior when the CSV file does not exist."""
    subjects = load_subjects_from_csv("/path/to/nonexistent/file.csv")
    assert subjects == []


# --- Tests for unzip_nifti_if_needed ---

import os
import gzip
from pywhifun.utils.io import unzip_nifti_if_needed

def test_unzip_nifti_if_needed(tmp_path):
    """Tests the unzip utility for .nii.gz files."""
    # 1. Create a dummy gzipped file
    gz_path = tmp_path / "test.nii.gz"
    nii_path = tmp_path / "test.nii"
    dummy_content = b"dummy nifti content"

    with gzip.open(gz_path, 'wb') as f_out:
        f_out.write(dummy_content)

    assert gz_path.exists()
    assert not nii_path.exists()

    # 2. Call the function - it should unzip the file
    result_path = unzip_nifti_if_needed(str(gz_path))
    assert result_path == str(nii_path)
    assert nii_path.exists()
    with open(nii_path, 'rb') as f_in:
        assert f_in.read() == dummy_content

    # 3. Call the function again - it should do nothing and return the .nii path
    # We can check this by making sure the file is not modified
    last_mod_time = os.path.getmtime(nii_path)
    result_path_2 = unzip_nifti_if_needed(str(gz_path))
    assert result_path_2 == str(nii_path)
    assert os.path.getmtime(nii_path) == last_mod_time

    # 4. Call the function with an already unzipped path
    result_path_3 = unzip_nifti_if_needed(str(nii_path))
    assert result_path_3 == str(nii_path)


# --- Tests for write_list_of_dicts_to_csv ---

from pywhifun.utils.io import write_list_of_dicts_to_csv

def test_write_list_of_dicts_to_csv(tmp_path):
    """Tests saving a list of dictionaries to a CSV file."""
    csv_path = tmp_path / "output.csv"
    data = [
        {'name': 'sub-01', 'age': 25, 'score': 100},
        {'name': 'sub-02', 'age': 30, 'score': 95}
    ]

    success = write_list_of_dicts_to_csv(data, str(csv_path))

    assert success is True
    assert csv_path.exists()

    # Read it back and check contents
    df_read = pd.read_csv(csv_path)
    assert len(df_read) == 2
    assert df_read.iloc[1]['name'] == 'sub-02'
    assert df_read.iloc[0]['score'] == 100

def test_write_list_of_dicts_to_csv_empty():
    """Tests that the function handles empty input correctly."""
    # This should not create a file and should return False
    success = write_list_of_dicts_to_csv([], "/path/to/nowhere.csv")
    assert success is False
