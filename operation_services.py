import math

from vector import Vector


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
