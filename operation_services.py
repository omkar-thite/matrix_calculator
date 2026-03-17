import math

from vector import Matrix, Vector


def parse_vectors_from_text_lines(lines):
    """Parse text rows like '1 2 3' into a list of Vector objects."""
    rows = []

    for line in lines:
        tokens = line.strip().split()
        if not tokens:
            raise ValueError("Each vector row must contain at least one numeric value.")

        try:
            rows.append([float(token) for token in tokens])
        except ValueError as exc:
            raise ValueError("Vector components must be numbers.") from exc

    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("All vectors must have the same number of components.")

    return [Vector(row) for row in rows]


def parse_vector_from_text_line(line):
    vectors = parse_vectors_from_text_lines([line])
    return vectors[0]


def parse_scalar_text(text):
    try:
        return float(text.strip())
    except ValueError as exc:
        raise ValueError("Scalar must be a numeric value.") from exc


def reduce_vectors(vectors, operation):
    """Reduce vectors by operation value: 'addition' or 'subtraction'."""
    if not vectors:
        raise ValueError("At least one vector is required.")

    if operation not in ("addition", "subtraction"):
        raise ValueError("Unsupported operation.")

    result = vectors[0]
    for vector in vectors[1:]:
        if operation == "addition":
            result += vector
        else:
            result -= vector

    return result


def compute_vector_binary_operation(vector_a, vector_b, operation):
    if operation == "dot":
        return "Dot product", Vector.dot(vector_a, vector_b)

    if operation == "cross":
        return "Cross product", Vector.cross(vector_a, vector_b)

    if operation == "angle":
        angle_radians = Vector.get_angle(vector_a, vector_b)
        return "Angle (degrees)", math.degrees(angle_radians)

    raise ValueError("Unsupported binary vector operation.")


def scalar_multiply_vector(vector, scalar):
    return vector * scalar


def get_vector_properties(vector):
    return {
        "vector": vector.coords,
        "dimension": vector.dim,
        "magnitude": vector.length,
        "theta (rad)": vector.get_theta(),
        "phi (rad)": vector.get_phi(),
    }


def parse_dimensions_text(text):
    try:
        rows_text, cols_text = text.strip().split()
        rows = int(rows_text)
        cols = int(cols_text)
    except ValueError as exc:
        raise ValueError("Dimensions must be in 'rows columns' integer format.") from exc

    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and columns must be positive integers.")

    return rows, cols


def parse_matrix_from_cells(cell_rows):
    if not cell_rows:
        raise ValueError("Matrix must contain at least one row.")

    width = len(cell_rows[0])
    if width == 0:
        raise ValueError("Matrix rows must contain at least one column.")

    parsed_rows = []
    for row in cell_rows:
        if len(row) != width:
            raise ValueError("All matrix rows must have the same number of columns.")

        parsed_row = []
        for value in row:
            text = str(value).strip()
            if text == "":
                raise ValueError("Matrix entries cannot be empty.")
            try:
                parsed_row.append(float(text))
            except ValueError as exc:
                raise ValueError("Matrix entries must be numeric.") from exc

        parsed_rows.append(parsed_row)

    return Matrix([Vector(row) for row in parsed_rows])


def matrix_add_subtract(matrices, operation):
    if not matrices:
        raise ValueError("At least one matrix is required.")

    if operation not in ("addition", "subtraction"):
        raise ValueError("Unsupported matrix reduction operation.")

    result = matrices[0]
    for matrix in matrices[1:]:
        if operation == "addition":
            result += matrix
        else:
            result -= matrix

    return result


def matrix_scalar_multiply(matrix, scalar):
    return matrix * scalar


def matrix_multiply(matrix_a, matrix_b):
    return matrix_a * matrix_b


def matrix_transpose(matrix):
    return matrix.transpose()


def matrix_gaussian_elimination(matrix):
    triangular = Matrix.triangularise(matrix)
    solved = Matrix.back(triangular)

    if not solved:
        raise ValueError("Gaussian elimination could not produce a valid result.")

    return Matrix([Vector(solved)])
