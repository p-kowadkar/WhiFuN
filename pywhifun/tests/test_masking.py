import numpy as np
import nibabel as nib
import pytest
import os
from numpy.testing import assert_allclose
from pywhifun.preprocessing.masking import skullstrip_image

@pytest.fixture
def tissue_map_files(tmp_path):
    """Creates dummy tissue probability maps and an anatomical image."""
    paths = {}
    affine = np.eye(4)

    # Create a simple anatomical image with values from 1 to 8
    anat_data = np.arange(1, 9, dtype=np.int16).reshape((2, 2, 2))
    anat_img = nib.Nifti1Image(anat_data, affine)
    paths['anat'] = tmp_path / "anat.nii"
    nib.save(anat_img, paths['anat'])

    # Create tissue maps where the sum of probabilities will create a clear mask
    # GM: high probability in the top-left-front voxel
    gm_data = np.array([[[0.8, 0.1], [0.1, 0.1]], [[0.1, 0.1], [0.1, 0.1]]], dtype=np.float32)
    # WM: high probability in the bottom-right-back voxel
    wm_data = np.array([[[0.1, 0.1], [0.1, 0.1]], [[0.1, 0.1], [0.1, 0.8]]], dtype=np.float32)
    # CSF: no high probability areas, just some low noise
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

    # Load the original data and the output data
    original_data = nib.load(tissue_map_files['anat']).get_fdata()
    skullstripped_data = nib.load(tissue_map_files['output']).get_fdata()

    # Expected mask:
    # Voxel (0,0,0): 0.8 + 0.1 + 0.1 = 1.0 > 0.5 -> Keep (value is 1)
    # Voxel (1,1,1): 0.1 + 0.8 + 0.1 = 1.0 > 0.5 -> Keep (value is 8)
    # All other voxels sum to 0.3 < 0.5 -> Mask out
    expected_data = np.array([[[1, 0], [0, 0]], [[0, 0], [0, 8]]], dtype=np.int16)

    assert_allclose(skullstripped_data, expected_data)


# --- Tests for create_csf_mask ---

from pywhifun.preprocessing.masking import create_csf_mask

def test_create_csf_mask(tmp_path):
    """Tests the creation of a binary CSF mask from a probability map."""
    # 1. Create a dummy CSF probability map
    csf_tpm_path = tmp_path / "csf_tpm.nii"
    csf_data = np.array([
        [0.1, 0.98],
        [0.8, 0.4]
    ], dtype=np.float32)
    affine = np.eye(4)
    nib.save(nib.Nifti1Image(csf_data, affine), csf_tpm_path)

    # 2. Create a dummy reference image (can be the same for this test)
    ref_path = csf_tpm_path

    # 3. Define output and call function
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

    # 4. Load the output mask and verify its contents
    mask_img = nib.load(output_path)
    mask_data = mask_img.get_fdata()

    expected_mask = np.array([
        [0, 1],
        [0, 0]
    ], dtype=np.int16)

    assert_allclose(mask_data, expected_mask)