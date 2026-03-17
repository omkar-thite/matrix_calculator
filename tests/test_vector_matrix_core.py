import math

import pytest

from vector import Matrix, Vector


def test_vector_rejects_non_numeric_coordinates():
    with pytest.raises(ValueError, match="Co-ordinates must be integers or floats"):
        Vector([1, "x"])


def test_vector_addition_rejects_mismatched_dimensions():
    with pytest.raises(ValueError, match="incompatible"):
        _ = Vector([1, 2]) + Vector([1, 2, 3])


def test_dot_product_rejects_mismatched_dimensions():
    with pytest.raises(ValueError, match="same dimension"):
        Vector.dot(Vector([1, 2]), Vector([1, 2, 3]))


def test_cross_product_requires_three_dimensions():
    with pytest.raises(ValueError, match="Invalid dimension"):
        Vector.cross(Vector([1, 2]), Vector([3, 4]))


def test_normalise_rejects_zero_vector():
    with pytest.raises(ValueError, match="Cannot normalise an empty vector"):
        Vector([0, 0, 0]).normalise()


def test_get_angle_returns_expected_radians():
    angle = Vector.get_angle(Vector([1, 0]), Vector([0, 1]))

    assert angle == pytest.approx(math.pi / 2)


def test_matrix_rejects_rows_with_mismatched_widths():
    with pytest.raises(ValueError, match="valid dimensions"):
        Matrix([Vector([1, 2]), Vector([3, 4, 5])])


def test_matrix_multiplication_rejects_incompatible_shapes():
    matrix_a = Matrix([Vector([1, 2]), Vector([3, 4])])
    matrix_b = Matrix([Vector([1, 2]), Vector([3, 4]), Vector([5, 6])])

    with pytest.raises(ValueError, match="Matrices of shape"):
        _ = matrix_a * matrix_b