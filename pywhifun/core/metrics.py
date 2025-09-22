import numpy as np
from typing import Tuple

def calculate_pairwise_dice_iou(net1: np.ndarray, net2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates pairwise Dice and IoU coefficients between two label maps.

    This function iterates through each unique label in `net1` and `net2`
    (ignoring the label 0) and computes the Dice and Intersection over Union (IoU)
    for each pair of labels. This mimics the core logic of the MATLAB
    `dice_iou.m` function.

    Args:
        net1: A numpy array representing the first label map.
        net2: A numpy array representing the second label map.

    Returns:
        A tuple containing two numpy arrays:
        - dice_matrix: A matrix where dice_matrix[i, j] is the Dice
          coefficient between label i from net1 and label j from net2. The
          matrix size is determined by the max label values.
        - iou_matrix: A matrix where iou_matrix[i, j] is the IoU
          coefficient between label i from net1 and label j from net2.
    """
    # Ensure input arrays are integer type
    net1 = np.asarray(net1, dtype=np.int32)
    net2 = np.asarray(net2, dtype=np.int32)

    # Get unique non-zero labels
    labels1 = np.unique(net1)
    labels1 = labels1[labels1 != 0]

    labels2 = np.unique(net2)
    labels2 = labels2[labels2 != 0]

    if labels1.size == 0 or labels2.size == 0:
        return np.array([]), np.array([])

    # Initialize matrices. The size is based on the max label value + 1
    # to allow for direct indexing by label number, which mimics the MATLAB
    # behavior (e.g., dice(i,j)).
    max_label1 = labels1.max()
    max_label2 = labels2.max()

    # +1 because label values are used as indices
    dice_matrix = np.zeros((max_label1 + 1, max_label2 + 1))
    iou_matrix = np.zeros((max_label1 + 1, max_label2 + 1))

    for i in labels1:
        # Find voxels for label i in net1. Using flatnonzero is efficient.
        net1_roi_indices = np.flatnonzero(net1 == i)
        len_net1_roi = len(net1_roi_indices)

        for j in labels2:
            # Find voxels for label j in net2
            net2_roi_indices = np.flatnonzero(net2 == j)
            len_net2_roi = len(net2_roi_indices)

            # Calculate intersection
            intersection = len(np.intersect1d(net1_roi_indices, net2_roi_indices, assume_unique=True))

            if intersection > 0:
                # Calculate Dice score
                dice_matrix[i, j] = 2.0 * intersection / (len_net1_roi + len_net2_roi)

                # Calculate IoU (Intersection over Union)
                union = len_net1_roi + len_net2_roi - intersection
                iou_matrix[i, j] = intersection / union

    return dice_matrix, iou_matrix
