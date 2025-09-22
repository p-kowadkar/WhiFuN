import numpy as np
from numpy.testing import assert_allclose
from pywhifun.core.metrics import calculate_pairwise_dice_iou

def test_dice_iou_simple_overlap():
    """Tests Dice/IoU calculation with simple partial overlap."""
    net1 = np.array([[1, 1, 0], [0, 0, 0]])
    net2 = np.array([[0, 1, 2], [0, 0, 2]])

    # Expected matrices (sized by max label values)
    # Max label in net1 is 1, max in net2 is 2. So size is (1+1, 2+1) = (2, 3)
    expected_dice = np.zeros((2, 3))
    expected_iou = np.zeros((2, 3))

    # Overlap between label 1 (net1) and label 1 (net2)
    # Intersection = 1, len1 = 2, len2 = 1
    # Dice = 2 * 1 / (2 + 1) = 0.666...
    # IoU = 1 / (2 + 1 - 1) = 0.5
    expected_dice[1, 1] = 2.0 / 3.0
    expected_iou[1, 1] = 0.5

    dice_matrix, iou_matrix = calculate_pairwise_dice_iou(net1, net2)

    assert_allclose(dice_matrix, expected_dice)
    assert_allclose(iou_matrix, expected_iou)

def test_dice_iou_no_overlap():
    """Tests Dice/IoU when there is no overlap between any labels."""
    net1 = np.array([[1, 1, 0], [0, 0, 0]])
    net2 = np.array([[0, 0, 2], [0, 2, 0]])

    expected_dice = np.zeros((2, 3))
    expected_iou = np.zeros((2, 3))

    dice_matrix, iou_matrix = calculate_pairwise_dice_iou(net1, net2)

    assert_allclose(dice_matrix, expected_dice)
    assert_allclose(iou_matrix, expected_iou)

def test_dice_iou_full_overlap():
    """Tests Dice/IoU for a perfect overlap between two labels."""
    net1 = np.array([[1, 1, 0], [0, 1, 0]])
    net2 = np.array([[2, 2, 0], [0, 2, 0]])

    expected_dice = np.zeros((2, 3))
    expected_iou = np.zeros((2, 3))

    # Overlap between label 1 (net1) and label 2 (net2)
    # Intersection = 3, len1 = 3, len2 = 3
    # Dice = 2 * 3 / (3 + 3) = 1.0
    # IoU = 3 / (3 + 3 - 3) = 1.0
    expected_dice[1, 2] = 1.0
    expected_iou[1, 2] = 1.0

    dice_matrix, iou_matrix = calculate_pairwise_dice_iou(net1, net2)

    assert_allclose(dice_matrix, expected_dice)
    assert_allclose(iou_matrix, expected_iou)

def test_dice_iou_multiple_labels():
    """Tests a more complex scenario with multiple labels."""
    net1 = np.array([[1, 1, 2], [0, 3, 2]])
    net2 = np.array([[1, 4, 4], [0, 3, 0]])

    # max_label1 = 3, max_label2 = 4. Size (3+1, 4+1) = (4, 5)
    expected_dice = np.zeros((4, 5))
    expected_iou = np.zeros((4, 5))

    # 1-1: int=1, s1=2, s2=1. dice=2/3, iou=1/2
    expected_dice[1, 1] = 2.0 / 3.0
    expected_iou[1, 1] = 0.5
    # 1-4: int=1, s1=2, s2=2. dice=2/4=0.5, iou=1/3
    expected_dice[1, 4] = 0.5
    expected_iou[1, 4] = 1.0 / 3.0
    # 2-4: int=1, s1=2, s2=2. dice=2/4=0.5, iou=1/3
    expected_dice[2, 4] = 0.5
    expected_iou[2, 4] = 1.0 / 3.0
    # 3-3: int=1, s1=1, s2=1. dice=2/2=1.0, iou=1/1=1.0
    expected_dice[3, 3] = 1.0
    expected_iou[3, 3] = 1.0

    dice_matrix, iou_matrix = calculate_pairwise_dice_iou(net1, net2)

    assert_allclose(dice_matrix, expected_dice)
    assert_allclose(iou_matrix, expected_iou)

def test_dice_iou_empty_input():
    """Tests behavior with empty (all-zero) label maps."""
    net1 = np.zeros((3, 3))
    net2 = np.array([[1, 1], [1, 1]])

    dice_matrix, iou_matrix = calculate_pairwise_dice_iou(net1, net2)

    assert dice_matrix.size == 0
    assert iou_matrix.size == 0
