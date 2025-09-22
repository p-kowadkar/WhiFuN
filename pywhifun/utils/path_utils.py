import os
import glob
from typing import List

def complete_filepath(*path_components: str) -> str:
    """
    Resolves a path constructed from components, potentially with wildcards.

    This function joins the given path components and expands any wildcards.
    - If the pattern resolves to a single file, it returns the full path to that file.
    - If the pattern resolves to multiple files, it returns their common parent directory.
    - If the pattern resolves to no files, it returns an empty string.

    This is a Python equivalent of the `complete_filepath.m` utility in WhiFuN.

    Args:
        *path_components: A variable number of strings that will be joined to
                          form the path pattern.

    Returns:
        The resolved file or directory path, or an empty string if no match is found.
    """
    if not path_components:
        return ""

    path_pattern = os.path.join(*path_components)

    matches = glob.glob(path_pattern)

    if len(matches) > 1:
        # Return the directory containing the matched files
        return os.path.dirname(matches[0])
    elif len(matches) == 1:
        # Return the full path to the single matched file
        return matches[0]
    else:
        # No matches found, return an empty string as per the original logic.
        # The calling code is responsible for handling the empty path case.
        return ""
