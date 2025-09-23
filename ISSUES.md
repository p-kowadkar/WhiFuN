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
