# PyWhiFuN Conversion Issues & Blockers

This document tracks major technical issues and conversion blockers that require user feedback or a decision on project direction.

## 1. fMRI Motion Correction / Realignment

- **Date**: 2025-09-23
- **MATLAB Function**: `whifun_realignment.m`
- **Core Dependency**: SPM12 (`spm_realign`)

### Description
The `whifun_realignment.m` function acts as a wrapper for SPM12's `spm_realign` function, which performs motion correction on 4D fMRI data. This process involves estimating the 6 rigid-body transformation parameters (3 translation, 3 rotation) for each volume relative to a reference volume and then reslicing the entire time series to align all volumes.

### The Block
The project instructions suggested using `nilearn.image` functions as a Python equivalent. However, after thorough review, it has been determined that **`nilearn` does not provide a direct, pure-Python equivalent for estimating motion parameters from a 4D fMRI series.**

`nilearn` has excellent tools for *applying* transformations (e.g., `resample_to_img`), but it does not have a built-in algorithm to *estimate* the realignment parameters from the image data itself. This estimation is the core of the `spm_realign` function.

### Potential Solutions (Requiring User Decision)

1.  **Use `nipype` Wrapper**: The standard way to perform this in the Python ecosystem is to use `nipype`, a library that provides Python wrappers for external neuroimaging tools like SPM, FSL, and AFNI.
    -   **Pro**: Would achieve 100% functional equivalence by calling the exact same SPM function.
    -   **Con**: This would require a full SPM12 installation in the execution environment, which is a very heavy dependency and may be outside the project's scope of creating a pure Python package.

2.  **Implement from Scratch**: Re-implementing a robust, production-quality motion estimation algorithm from scratch is a massive undertaking, equivalent to a PhD project in itself, and is not feasible within the scope of this project.

3.  **Use other Python Registration Libraries**: Libraries like `DiPy` or `SimpleITK` have image registration algorithms. It might be possible to adapt one of them for this purpose, but it would not be a direct equivalent of the SPM algorithm and would require significant research and development to validate. Scientific equivalence would not be guaranteed.

### Proposed Temporary Solution (Implemented)

To allow the rest of the pipeline conversion to proceed, I have implemented a **placeholder stub** for the `realign_image` function. This stub:
- Logs a prominent `WARNING` that this critical step is not being performed.
- Copies the input NIfTI file to the expected output location.
- Creates a dummy motion parameter file (`rp_*.txt`) filled with zeros.

This allows the downstream pipeline steps (like FD calculation) to run without crashing, but **no actual motion correction is being performed.**

**Requested Action:** Please review the potential solutions and advise on the preferred long-term strategy for this function. For now, I will proceed with the placeholder stub.

---

## 2. Anatomical Tissue Segmentation

- **Date**: 2025-09-23
- **MATLAB Function**: `whifun_segment.m`
- **Core Dependency**: SPM12 (`spm.spatial.preproc`)

### Description
The `whifun_segment.m` function is a wrapper for SPM12's powerful unified segmentation routine. This single command performs bias correction, segments the brain into 6 tissue classes (saving GM, WM, and CSF probability maps), and calculates the deformation fields for normalizing the image to MNI space.

### The Block
Similar to the realignment issue, there is **no direct, pure-Python equivalent for SPM's segmentation algorithm within the `nilearn` library**. The user's project notes suggested `nilearn.image.clean_img`, but this function is for fMRI time-series denoising, not anatomical tissue segmentation.

Standard Python neuroimaging pipelines (`fMRIPrep`, `CPAC`) achieve this by using wrappers around external tools like SPM, FSL (`FAST`), or ANTs. A pure-Python implementation would require a dedicated, advanced library for this specific task, which is not part of the current dependency list.

### Potential Solutions (Requiring User Decision)

1.  **Use `nipype` Wrapper**: Call SPM's segmentation via `nipype`. This would provide perfect functional equivalence.
    -   **Con**: Requires a full SPM12 installation in the execution environment.

2.  **Use a dedicated Python library**: Libraries like `ANTsPy` offer advanced registration and segmentation tools, but they are heavy dependencies and their results would differ from SPM's, requiring a full re-validation of the pipeline.

### Proposed Temporary Solution (Implemented)

To allow pipeline development to continue, I have implemented a **placeholder stub** for the `segment_image` function. This stub:
- Logs a prominent `WARNING` that segmentation is not being performed.
- Creates dummy output files that are expected by downstream steps. This includes empty NIfTI files for the tissue maps (`c1*`, `c2*`, `c3*`) and the deformation field (`y_*`).

**Requested Action:** Please advise on the preferred long-term strategy for tissue segmentation. I will proceed with the placeholder stub for now.

---

## 3. Coregistration

- **Date**: 2025-09-24
- **MATLAB Function**: `whifun_coreg.m`
- **Core Dependency**: SPM12 (`spm.spatial.coreg.estimate`)

### Description
The `whifun_coreg.m` function is a wrapper for SPM12's coregistration module. It *estimates* the affine transformation required to align a source image (mean fMRI) to a reference image (anatomical T1w). It then applies this transformation by modifying the headers of the fMRI time series in-place.

### The Block
This is the third major preprocessing step (after realignment and segmentation) that does not have a direct, pure-Python equivalent in the `nilearn` library. `nilearn` can apply known transformations but lacks a high-level function to *estimate* the optimal registration between two images with different modalities (e.g., T1w and EPI). This estimation is a complex optimization problem that is handled by dedicated external tools.

### Potential Solutions (Requiring User Decision)

1.  **Use `nipype` Wrapper**: Call SPM's coregistration via `nipype`. This would provide perfect functional equivalence.
    -   **Con**: Requires a full SPM12 installation in the execution environment.
2.  **Use other Python Registration Libraries**: Libraries like `ANTsPy`, `SimpleITK`, or `DiPy` have powerful registration algorithms.
    -   **Pro**: A pure Python solution would be possible.
    -   **Con**: The results would differ from SPM's, requiring re-validation. These are also heavy dependencies.

### Proposed Temporary Solution (Implemented)

To allow pipeline development to continue, I will implement a **placeholder stub** for the `coregister_image` function. This stub:
- Logs a prominent `WARNING` that coregistration is not being performed.
- Returns `True` to signal success, allowing the pipeline to proceed, but does not modify any files.

**Requested Action:** Please advise on the preferred long-term strategy for coregistration. I will proceed with the placeholder stub for now.
