import numpy as np
import nibabel as nib
import pytest
import os
from pywhifun.preprocessing.segmentation import segment_image_stub

def test_segment_image_stub(tmp_path):
    """
    Tests that the segmentation stub correctly creates all dummy output files.
    """
    # 1. Create a dummy input anatomical file
    anat_filename = "t1w.nii.gz"
    anat_path = tmp_path / anat_filename

    # Create a dummy 3D nifti image
    data = np.zeros((10, 10, 10), dtype=np.int16)
    img = nib.Nifti1Image(data, np.eye(4))
    nib.save(img, anat_path)

    # 2. Call the stub function
    output_files = segment_image_stub(str(anat_path))

    # 3. Check that the output dictionary has the correct keys
    expected_keys = ['gm', 'wm', 'csf', 'fwd_def', 'inv_def']
    assert sorted(list(output_files.keys())) == sorted(expected_keys)

    # 4. Check that all the files were actually created on disk
    for key, filepath in output_files.items():
        assert os.path.exists(filepath), f"Dummy file for '{key}' was not created at {filepath}"

    # 5. Check that one of the created files is a valid NIfTI file
    # This implicitly tests the save_nifti call within the stub
    loaded_gm = nib.load(output_files['gm'])
    assert loaded_gm.shape == data.shape
    assert loaded_gm.get_data_dtype() == np.float32 # The stub creates float32 data

    # 6. Check that the filenames are correct
    assert output_files['gm'].endswith(f"c1{anat_filename}")
    assert output_files['fwd_def'].endswith(f"y_{anat_filename}")
