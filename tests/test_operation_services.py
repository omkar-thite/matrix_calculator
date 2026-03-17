import math

import pytest

from operation_services import (
    compute_vector_binary_operation,
    get_vector_properties,
    matrix_add_subtract,
    matrix_gaussian_elimination,
    matrix_multiply,
    matrix_scalar_multiply,
    matrix_transpose,
    parse_dimensions_text,
    parse_matrix_from_cells,
    parse_scalar_text,
    parse_vector_from_text_line,
    parse_vectors_from_text_lines,
    reduce_vectors,
    scalar_multiply_vector,
)
from vector import Matrix, Vector


def assert_vector_coords(actual, expected):
    assert actual.coords == pytest.approx(expected)


def assert_matrix_coords(actual, expected):
    assert len(actual.rows) == len(expected)
    for row, expected_row in zip(actual.rows, expected):
        assert row.coords == pytest.approx(expected_row)


def test_parse_vectors_from_text_lines_parses_float_components():
    vectors = parse_vectors_from_text_lines(["1 2 3", "4.5 -2 0"])

    assert len(vectors) == 2
    assert_vector_coords(vectors[0], [1.0, 2.0, 3.0])
    assert_vector_coords(vectors[1], [4.5, -2.0, 0.0])


def test_parse_vectors_from_text_lines_rejects_non_numeric_values():
    with pytest.raises(ValueError, match="Vector components must be numbers"):
        parse_vectors_from_text_lines(["1 two 3"])


def test_parse_vectors_from_text_lines_rejects_mismatched_dimensions():
    with pytest.raises(ValueError, match="same number of components"):
        parse_vectors_from_text_lines(["1 2", "3 4 5"])


def test_parse_vector_from_text_line_returns_single_vector():
    vector = parse_vector_from_text_line("3 -1 4")

    assert_vector_coords(vector, [3.0, -1.0, 4.0])


def test_parse_scalar_text_strips_whitespace():
    assert parse_scalar_text("  2.5  ") == pytest.approx(2.5)


def test_parse_scalar_text_rejects_invalid_text():
    with pytest.raises(ValueError, match="Scalar must be a numeric value"):
        parse_scalar_text("abc")


def test_reduce_vectors_addition_and_subtraction():
    vectors = [Vector([1, 2]), Vector([3, 4]), Vector([5, 6])]

    added = reduce_vectors(vectors, "addition")
    subtracted = reduce_vectors(vectors, "subtraction")

    assert_vector_coords(added, [9, 12])
    assert_vector_coords(subtracted, [-7, -8])


def test_reduce_vectors_validates_input():
    with pytest.raises(ValueError, match="At least one vector is required"):
        reduce_vectors([], "addition")

    with pytest.raises(ValueError, match="Unsupported operation"):
        reduce_vectors([Vector([1, 2])], "multiply")


def test_compute_vector_binary_operation_supports_dot_cross_and_angle():
    label, dot = compute_vector_binary_operation(Vector([1, 2]), Vector([3, 4]), "dot")
    assert label == "Dot product"
    assert dot == pytest.approx(11)

    label, cross = compute_vector_binary_operation(Vector([2, 1, 5]), Vector([1, 2, 5]), "cross")
    assert label == "Cross product"
    assert_vector_coords(cross, [-5, -5, 3])

    label, angle = compute_vector_binary_operation(Vector([1, 0]), Vector([0, 1]), "angle")
    assert label == "Angle (degrees)"
    assert angle == pytest.approx(90.0)


def test_compute_vector_binary_operation_rejects_unknown_operation():
    with pytest.raises(ValueError, match="Unsupported binary vector operation"):
        compute_vector_binary_operation(Vector([1, 0]), Vector([0, 1]), "project")


def test_scalar_multiply_vector_returns_scaled_vector():
    result = scalar_multiply_vector(Vector([1, -2, 3]), 2)

    assert_vector_coords(result, [2, -4, 6])


def test_get_vector_properties_returns_expected_values():
    vector = Vector([3, 4, 12])

    properties = get_vector_properties(vector)

    assert properties["vector"] == [3, 4, 12]
    assert properties["dimension"] == 3
    assert properties["magnitude"] == pytest.approx(13)
    assert properties["theta (rad)"] == pytest.approx(math.acos(12 / 13))
    assert properties["phi (rad)"] == pytest.approx(math.acos(3 / 13))


def test_parse_dimensions_text_parses_valid_dimensions():
    assert parse_dimensions_text("2 3") == (2, 3)


@pytest.mark.parametrize(
    "value, message",
    [
        ("2", "Dimensions must be in 'rows columns' integer format"),
        ("2.5 3", "Dimensions must be in 'rows columns' integer format"),
        ("0 3", "Rows and columns must be positive integers"),
        ("2 -1", "Rows and columns must be positive integers"),
    ],
)
def test_parse_dimensions_text_validates_input(value, message):
    with pytest.raises(ValueError, match=message):
        parse_dimensions_text(value)


def test_parse_matrix_from_cells_parses_numeric_grid():
    matrix = parse_matrix_from_cells([["1", "2.5"], [3, "4"]])

    assert_matrix_coords(matrix, [[1.0, 2.5], [3.0, 4.0]])


@pytest.mark.parametrize(
    "cells, message",
    [
        ([], "Matrix must contain at least one row"),
        ([[]], "Matrix rows must contain at least one column"),
        ([["1", "2"], ["3"]], "All matrix rows must have the same number of columns"),
        ([["1", ""], ["3", "4"]], "Matrix entries cannot be empty"),
        ([["1", "x"]], "Matrix entries must be numeric"),
    ],
)
def test_parse_matrix_from_cells_validates_input(cells, message):
    with pytest.raises(ValueError, match=message):
        parse_matrix_from_cells(cells)


def test_matrix_add_subtract_supports_addition_and_subtraction():
    matrices = [
        Matrix([Vector([1, 2]), Vector([3, 4])]),
        Matrix([Vector([5, 6]), Vector([7, 8])]),
        Matrix([Vector([1, 1]), Vector([1, 1])]),
    ]

    added = matrix_add_subtract(matrices, "addition")
    subtracted = matrix_add_subtract(matrices, "subtraction")

    assert_matrix_coords(added, [[7, 9], [11, 13]])
    assert_matrix_coords(subtracted, [[-5, -5], [-5, -5]])


def test_matrix_add_subtract_validates_input():
    with pytest.raises(ValueError, match="At least one matrix is required"):
        matrix_add_subtract([], "addition")

    with pytest.raises(ValueError, match="Unsupported matrix reduction operation"):
        matrix_add_subtract([Matrix([Vector([1, 2])])], "multiply")


def test_matrix_scalar_multiply_scales_each_entry():
    matrix = Matrix([Vector([1, 2]), Vector([3, 4])])

    result = matrix_scalar_multiply(matrix, 3)

    assert_matrix_coords(result, [[3, 6], [9, 12]])


def test_matrix_multiply_multiplies_compatible_matrices():
    matrix_a = Matrix([Vector([1, 2, 3]), Vector([4, 5, 6])])
    matrix_b = Matrix([Vector([7, 8]), Vector([9, 10]), Vector([11, 12])])

    result = matrix_multiply(matrix_a, matrix_b)

    assert_matrix_coords(result, [[58, 64], [139, 154]])


def test_matrix_transpose_swaps_rows_and_columns():
    matrix = Matrix([Vector([1, 2, 3]), Vector([4, 5, 6])])

    result = matrix_transpose(matrix)

    assert_matrix_coords(result, [[1, 4], [2, 5], [3, 6]])


def test_matrix_gaussian_elimination_returns_solution_row_matrix():
    matrix = Matrix([Vector([2, 1, 5]), Vector([0, 3, 6])])

    result = matrix_gaussian_elimination(matrix)

    assert_matrix_coords(result, [[1.5, 2.0]])


def test_matrix_gaussian_elimination_raises_for_singular_system():
    matrix = Matrix([Vector([1, 1, 2]), Vector([2, 2, 4])])

    with pytest.raises(ValueError, match="Gaussian elimination could not produce a valid result"):
        matrix_gaussian_elimination(matrix)