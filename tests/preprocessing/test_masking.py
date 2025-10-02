import pytest
import numpy as np
import nibabel as nib
import os
from numpy.testing import assert_allclose

# Imports from the original new test file
from pywhifun.preprocessing.masking import skullstrip_stub, create_csf_mask_stub

# Imports from the old, misplaced test file
from pywhifun.preprocessing.masking import skullstrip_image, create_csf_mask

# --- Tests for the new stubs ---

def test_skullstrip_stub():
    """
    Tests that the skullstrip_stub runs and returns the expected fake file path.
    """
    anat_path = "/fake/anat.nii"
    segmentation_files = {} # Stub doesn't use this

    result = skullstrip_stub(anat_path, segmentation_files)

    assert isinstance(result, str), "skullstrip_stub should return a string path"
    assert "brain_anat.nii" in result, "Path should contain the expected filename"

def test_create_csf_mask_stub():
    """
    Tests that the create_csf_mask_stub runs and returns the expected fake file path.
    """
    anat_path = "/fake/anat.nii"
    segmentation_files = {} # Stub doesn't use this
    params = {} # Stub doesn't use this

    result = create_csf_mask_stub(anat_path, segmentation_files, params)

    assert isinstance(result, str), "create_csf_mask_stub should return a string path"
    assert "csf_mask.nii" in result, "Path should contain the expected filename"

# --- Tests from the old, preserved test_masking.py ---

@pytest.fixture
def tissue_map_files(tmp_path):
    """Creates dummy tissue probability maps and an anatomical image."""
    paths = {}
    affine = np.eye(4)

    anat_data = np.arange(1, 9, dtype=np.int16).reshape((2, 2, 2))
    anat_img = nib.Nifti1Image(anat_data, affine)
    paths['anat'] = tmp_path / "anat.nii"
    nib.save(anat_img, paths['anat'])

    gm_data = np.array([[[0.8, 0.1], [0.1, 0.1]], [[0.1, 0.1], [0.1, 0.1]]], dtype=np.float32)
    wm_data = np.array([[[0.1, 0.1], [0.1, 0.1]], [[0.1, 0.1], [0.1, 0.8]]], dtype=np.float32)
    csf_data = np.full((2, 2, 2), 0.1, dtype=np.float32)

    for name, data_array in [('gm', gm_data), ('wm', wm_data), ('csf', csf_data)]:
        img = nib.Nifti1Image(data_array, affine)
        paths[name] = tmp_path / f"{name}.nii"
        nib.save(img, paths[name])

    paths['output'] = tmp_path / "brain.nii"
    return paths

def test_skullstrip_image(tissue_map_files):
    """Tests the skull-stripping logic based on tissue probability maps."""
    success = skullstrip_image(
        anat_path=str(tissue_map_files['anat']),
        gm_path=str(tissue_map_files['gm']),
        wm_path=str(tissue_map_files['wm']),
        csf_path=str(tissue_map_files['csf']),
        output_path=str(tissue_map_files['output']),
        threshold=0.5
    )

    assert success is True
    assert os.path.exists(tissue_map_files['output'])

    original_data = nib.load(tissue_map_files['anat']).get_fdata()
    skullstripped_data = nib.load(tissue_map_files['output']).get_fdata()

    expected_data = np.array([[[1, 0], [0, 0]], [[0, 0], [0, 8]]], dtype=np.int16)

    assert_allclose(skullstripped_data, expected_data)

def test_create_csf_mask(tmp_path):
    """Tests the creation of a binary CSF mask from a probability map."""
    csf_tpm_path = tmp_path / "csf_tpm.nii"
    csf_data = np.array([[0.1, 0.98], [0.8, 0.4]], dtype=np.float32)
    affine = np.eye(4)
    nib.save(nib.Nifti1Image(csf_data, affine), csf_tpm_path)

    ref_path = csf_tpm_path

    output_path = tmp_path / "csf_mask.nii"
    threshold = 0.9

    success = create_csf_mask(
        csf_tpm_path=str(csf_tpm_path),
        ref_img_path=str(ref_path),
        output_path=str(output_path),
        threshold=threshold
    )

    assert success is True
    assert output_path.exists()

    mask_img = nib.load(output_path)
    mask_data = mask_img.get_fdata()

    expected_mask = np.array([[0, 1], [0, 0]], dtype=np.int16)

    assert_allclose(mask_data, expected_mask)