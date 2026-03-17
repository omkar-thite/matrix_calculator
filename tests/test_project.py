from vector import Matrix, Vector
from main import matrix_add, matrix_subtract, matrix_scalar_multiplication

tolerance = 0.00000000000001


def assert_matrix_coords(actual, expected):
    for i in range(len(actual.rows)):
        for j in range(len(actual.rows[0].coords)):
            assert abs(actual.rows[i].coords[j] - expected.rows[i].coords[j]) < tolerance

def test_matrix_multiplication():
    matrix1 = Matrix([Vector([2, 3, 4]), Vector([1, 0, 2])])
    matrix2 = Matrix([Vector([1, 2, 4, 8]), Vector([7, 5, -4, 12]), Vector([1, -2, 6, 4])])
    
    product = Matrix([Vector([27, 11, 20, 68]), Vector([3, -2, 16, 16])])

    result = matrix1 * matrix2
    assert_matrix_coords(result, product)


def test_matrix_add():
    matrix1 = Matrix([Vector([2, 3, 4, 4]), Vector([1, 0, 2.1, 1]), Vector([1, -2.2, 2, 1])])
    matrix2 = Matrix([Vector([1, 2, 4, 8]), Vector([7, 5.3, -4, 12]), Vector([1, -2, 6.4, 4])])

    sum = Matrix([Vector([3, 5, 8, 12]), Vector([8, 5.3, -1.9, 13]), Vector([2, -4.2, 8.4, 5])])

    result = matrix_add(matrix1, matrix2)
    assert_matrix_coords(result, sum)


def test_matrix_subtract():
    matrix1 = Matrix([Vector([2, 3, 4, 4]), Vector([1, 0, 2.1, 1]), Vector([1, -2.2, 2, 1])])
    matrix2 = Matrix([Vector([1, 2, 4, 8]), Vector([7, 5.3, -4, 12]), Vector([1, -2, 6.4, 4])])


    difference = Matrix([Vector([1, 1, 0, -4]), Vector([-6, -5.3, 6.1, -11]), Vector([0,-0.2, -4.4, -3])])

    result = matrix_subtract(matrix1, matrix2)
    assert_matrix_coords(result, difference)
    
def test_matrix_scalar_multiplication():
    matrix1 = Matrix([Vector([2, 3, 4, 4]), Vector([1, 0, 2.1, 1]), Vector([1, -2.2, 2, 1])])
    scalar = 2

    product = Matrix([Vector([4, 6, 8, 8]), Vector([2, 0, 4.2, 2]), Vector([2, -4.4, 4, 2])])

    result = matrix_scalar_multiplication(matrix1, scalar)
    assert_matrix_coords(result, product)
    
def test_cross_product():
    u = Vector([2, 1, 5])
    v = Vector([1, 2, 5])
    cross = Vector([-5, -5, 3])
    result = Vector.cross(u, v)

    
    for i in range(result.dim):
        assert abs(result.coords[i] - cross.coords[i]) < tolerance


def test_dot_product():
    u = Vector([2, 1, 5])
    v = Vector([1, 2, 5])
    dot = 29
    result = Vector.dot(u, v)
    
    assert abs(result - dot) < tolerance

    




