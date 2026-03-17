import math
import logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('vector.log')
formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class Vector:
    """
    Represents a mathematical vector with basic operations 
    (e.g., addition, subtraction, angle calculation).
    """
    def __init__(self, coords):
        """
        Initialize the vector.
        :param coords: A list or tuple of numeric values.
        """
        if not isinstance(coords, (list, tuple)):
            logger.error('coords is not of type list or tuple')
            raise TypeError("coords must be a list or a tuple")

        self.coords = coords

        self.dim = len(coords)
        
        # length of vector
        summ = 0   
        for x in coords:
            summ += (x**2)     
        self.length = math.sqrt(summ)    
        logger.info(f'Vector object with coordinates {self.coords} is created.')

    # Getter for coords
    @property
    def coords(self):
        """
        Retrieves the coordinate list of the vector.
        
        :return: A list or tuple of numeric coordinates.
        """
        return self._coords
    
    # Setter function for coords
    @coords.setter
    def coords(self, coords):
        """
        Sets the coordinates of the vector with validation.
        
        :param coords: A list of numeric coordinates.
        :raises ValueError: If any coordinate is not a float or int.
        """
        for i in coords:
            if not isinstance(i, (int, float)):
                logger.error("Co-ordinates must be integers or floats.")
                raise ValueError("Co-ordinates must be integers or floats.")

        self._coords = coords
    
    
    @classmethod
    def dot(cls, a, b):
        """
        Compute the dot product of two vectors.
        
        :param a: The first vector.
        :param b: The second vector.
        :return: The dot product as a float.
        :raises TypeError: If inputs are not Vector objects.
        :raises ValueError: If vectors have different dimensions.
        """

        if not isinstance(a, Vector) or not isinstance(b, Vector):
            logger.error("Invalid inputs to dot product, expected Vectors.")
            raise TypeError("Invalid inputs to dot product, expected Vectors.")

        dim_1 = a.dim
        dim_2 = b.dim
        
        if dim_1 != dim_2:
            logger.error("Expected vectors of same dimension for dot product operation.")
            raise ValueError("Expected vectors of same dimension for dot product operation.")

        product = 0.0
        for i in range(dim_1):
            product += (a.coords[i] * b.coords[i])
        return product

    
    # 2x2 Determinant
    @classmethod
    def det(cls, a, b):
        """
        Compute the determinant of a 2x2 matrix formed by two vectors.
        
        :param a: A list representing the first row.
        :param b: A list representing the second row.
        :return: The determinant as a float.
        """
        return (a[0] * b[1]) - (a[1] * b[0])

  
    # 3D vector only cross product
    @classmethod
    def cross(cls, p, q):
        """
        Compute the cross product of two 3D vectors.
        
        :param p: The first vector.
        :param q: The second vector.
        :return: A new Vector representing the cross product.
        :raises TypeError: If inputs are not Vector objects.
        :raises ValueError: If vectors are not 3D or have different dimensions.
        """
        if not isinstance(p, Vector) or not isinstance(q, Vector):
            logger.error("Invalid inputs to cross product, expected Vectors.")
            raise TypeError("Invalid inputs to cross product, expected Vectors.")

        dim_1 = p.dim
        dim_2 = q.dim
        
        if dim_1 != dim_2:
            logger.debug('Vectors of different dimensions passed to 3D cross product operation.')
            raise ValueError("Expected vectors of same dimension for 3D cross product operation.")
        
        if p.dim != 3:
            logger.debug('Vectors that are not 3 dimensional are passed to 3D cross product operation.')
            raise ValueError("Invalid dimension of vectors for 3D cross product operation.")

            
        a = p.coords
        b = q.coords
        # c will store crossed values
        c = []

        # Over the first row
        for i in range(3): 
            # New trimmed lists for every iteration 
            trim_a = []
            trim_b = []

            # trim a and b
            for j in range(3): 
                if (i != j):     
                    trim_a.append(a[j])
                    trim_b.append(b[j])

            c.append(((-1)**i) * Vector.det(trim_a, trim_b))


        return Vector(c) 
    
    
    def get_phi(self):
        """
        Computes the angle φ of the vector.
        
        In 2D: Uses math.atan(y / x).
        In 3D: Uses math.acos(x / length).
        
        :return: Angle φ in radians.
        """
        if self.dim == 2:
            return math.atan(self.coords[1] / self.coords[0])
        if self.dim == 3:
            return math.acos(self.coords[0] / self.length)
    
    def get_theta(self):
        """
        Computes the angle θ of the vector in 3D using math.acos(z / length).
        
        :return: Angle θ in radians if the vector is 3D, otherwise None.
        """
        if self.dim == 3:
            return math.acos(self.coords[2] / self.length)


    def __str__(self):
        """
        Represent the vector as a string.
        
        :return: A string representation of the vector.
        """
        return f"{self.coords}, r = {self.length:.2f}"
        

    def __add__(self,other):
        """
        Add two vectors.
        
        :param other: The vector to add.
        :return: A new Vector representing the sum.
        :raises TypeError: If other is not a Vector.
        :raises ValueError: If vectors have different dimensions.
        """
        
        if not isinstance(other, Vector):
            logger.error(f'Invalid input of type {type(other)} passed to + operand.')
            raise TypeError("Can only add Vector with another Vector")

        dim_1 = self.dim
        dim_2 = other.dim
        
        if dim_1 != dim_2:
            logger.error(f'Vectors of {self.dim} and {other.dim} are incompatible for + operand.')
            raise ValueError("Vectors of {self.dim} and {other.dim} are incompatible for + operand.")
            
        added_coords = [self.coords[i] + other.coords[i] for i in range(dim_1)]
        
        return Vector(added_coords)
            
    
    def __sub__(self, other):
        """
        Subtract one vector from another.
        
        :param other: The vector to subtract.
        :return: A new Vector representing the difference.
        :raises TypeError: If other is not a Vector.
        :raises ValueError: If vectors have different dimensions.
        """
        
        if not isinstance(other, Vector):
            logger.error(f'Invalid input of type {type(other)} passed to - operand.')
            raise TypeError("Can only subtract Vector with another Vector")

        dim_1 = self.dim
        dim_2 = other.dim
        
        if dim_1 != dim_2:
            logger.error(f'Vectors of {self.dim} and {other.dim} are incompatible for - operand.')
            raise ValueError("Can't subtract vectors of different dimension!")

        subtracted_coords = [self.coords[i] - other.coords[i] for i in range(dim_1)]
        
        return Vector(subtracted_coords)

          
    def __mul__(self, other):
        """
        Perform elementwise multiplication between two vectors or scalar multiplication.
        
        :param other: The vector or scalar to multiply with.
        :return: A new Vector representing the elementwise product.
        :raises TypeError: If other is not a Vector.
        :raises ValueError: If vectors have different dimensions.
        """
        # Scalar multiplication if other is scalar
        if isinstance(other, (int, float)):
            product = [0 for _ in range(self.dim)]
            for i in range(self.dim):
                product[i] = self.coords[i] * other
            return Vector(product)

        # Elementwise multiplication if other is vector
        elif not isinstance(other, Vector):
            logger.error(f'Object of type {type(other)} passed to * operand')
            raise TypeError("Expected Vector for * operation with a Vector.")
        
        else:
            dim_1 = self.dim
            dim_2 = other.dim
            
            if dim_1 != dim_2:
                logger.error(f'Vector of incompatible dimensions {self.dim} and {other.dim} passed for * operation.')
                raise ValueError("Can't multiply vectors elementwise with different dimension!")
            
            multiplied = [self.coords[i] + other.coords[i] for i in range(dim_1)]
        
            return Vector(multiplied)



    def normalise(self):
        """
        Normalize the vector to have a length of 1.
        
        :return: A new normalized Vector.
        :raises ValueError: If the vector is a zero vector.
        """
        if self.length == 0:
            logger.error('Empty vector passed to normalize()')
            raise ValueError("Cannot normalise an empty vector.")
        return self * (1 / self.length)
       

    # Get angle between two vectors
    @classmethod
    def get_angle(cls, vector1, vector2):
        """
        Calculate the angle between two vectors.
        
        :param vector1: The first vector.
        :param vector2: The second vector.
        :return: The angle in radians.
        :raises ValueError: If inputs are not Vector objects.
        """
        if not isinstance(vector1, Vector) and not isinstance(vector2, Vector):
            logger.error(f'Vectors of {type(vector1)} and {type(vector2)} are incompatible for get_angle().')
            raise ValueError("Expected Vectors for this operation.")
        
        product = cls.dot(vector1, vector2)
        cos = product / (vector1.length * vector2.length)

        # provision for rounding errors
        if cos > 1:
            cos = 1
        if cos < -1:
            cos = -1

        return math.acos(cos)


class Matrix(Vector):
    # Matrix is list of Vector objects i.e, rows of given matrix are Vector objects
    def __init__(self, vectors):

        if not isinstance(vectors, (list, tuple)):
            logger.error('arg vectors passed to Matrix is not of type list or tuple')
            raise TypeError(f"Expected list or tuple of Vector objects but received {type(vectors)} object.")

        # Populate the matrix
        self.rows = Matrix.populate_matrix(vectors)
        self.m = len(self.rows)
        self.n = vectors[0].dim

           
    
    def populate_matrix(vectors):
        rows = []
        print(type(vectors[0]))
        n = vectors[0].dim

        for vector in vectors:
            if vector.dim != n:
                logger.error('One or serveral of row vectors passed to Matrix() are not of same dimensions.')
                raise ValueError(f"{vector.coords} doesn't have valid dimensions.")
            
            rows.append(vector)
        return rows


    @classmethod
    def get_matrix(cls):
        """
        Creates a Matrix object by taking user input from the command line.

        :return: A Matrix object with user-defined dimensions and values.
        :raises ValueError: If the input is invalid or not properly formatted.
        """
        rows = []

        try:
            m, n = input("Enter dimensions in format rows<space>columns: ").split()
            m  = int(m)
            n = int(n)

            for i in range(m):
                row = input(f"row {i}: ").strip().split()
                tmp = []

                # Convert to floats        
                for j in range(n):
                    tmp.append(float(row[j]))

                rows.append(Vector(tmp))
        
        except (ValueError, IndexError, TypeError):
            logger.error(f'Wrong type of input given as entries of matrix: {type(row[j])}')
            raise ValueError("Expected int or float as input.")
        else:
            logger.info(f'Matrix of shape ({len(rows), len(rows[0])}) created.')
            return Matrix(rows)


    def __add__(self, other):
        """
        Adds two matrices element-wise.

        :param other: A Matrix object to be added.
        :return: A new Matrix object representing the sum.
        :raises ValueError: If either matrix is empty or dimensions do not match.
        """

        if self.m == 0 or other.m == 0:
            logger.error('Empty values passed to + operand.')
            raise ValueError('Empty Matrix cannot be operated.')
        
        added = [self.rows[i] + other.rows[i] for i in range(self.m)]
        
        return (Matrix(added))


    def __sub__(self, other):
        """
        Subtracts one matrix from another element-wise.

        :param other: A Matrix object to be subtracted.
        :return: A new Matrix object representing the difference.
        :raises ValueError: If either matrix is empty or dimensions do not match.
        """

        if self.m == 0 or other.m == 0:
            logger.error('Empty matrix passed to - operation.')
            raise ValueError('Empty Matrix cannot be operated.')
    
        result = [self.rows[i] - other.rows[i] for i in range(self.m)]
        
        return Matrix(result)


    def __str__(self):
        
        string = "["
        for i in self.rows:
            string += f"  {i.coords}\n"
        string = string.rstrip(string[-1])
        string += " ]\n"
        return string


    def __mul__(self,other):
        """
        Multiplies a matrix by a scalar or another matrix.

        :param other: A scalar (int or float) for scalar multiplication or a Matrix object for matrix multiplication.
        :return: A new Matrix object representing the product.
        :raises ValueError: If the matrices cannot be multiplied due to incompatible dimensions.
        :raises TypeError: If the operand is neither a scalar nor a Matrix object.
        """

        # Scalar multiplication
        if isinstance(other, (int, float)):
            product = [row * other for row in self.rows]
            return Matrix(product)
        
        # Multiplication of two matrices
        elif isinstance(other, Matrix):
            if self.n != other.m:
                logger.error(f'Matrices of shape {(self.m, self.n)} and {(other.m, other.n)} passed to * operation')
                raise ValueError("Matrices of shape {(self.m, self.n)} and {(other.m, other.n)} passed to * operation")

            product = []
            transpose = other.transpose()
            
            for i in range(self.m):
                tmp = []
                for j in range(other.n):
                    try: 
                        tmp.append(Vector.dot(self.rows[i], transpose.rows[j]))
                    except ValueError:
                        raise RuntimeError("Error in dot product operation!")
                product.append(Vector(tmp))
            
            return Matrix(product)
        

    def transpose(self):
        """
        Transposes the matrix by swapping rows with columns.

        :return: A new Matrix object representing the transposed matrix.
        """

        transposed = [[0] * self.m for _ in range(self.n)]
        
        for i in range(len(self.rows)):
            for j in range(self.n):
                    transposed[j][i] = self.rows[i].coords[j]

        return Matrix([Vector(row) for row in transposed])
    

    # Lower triangularise
    def triangularise(matrix):
        """
        Converts a matrix into its lower triangular form using Gaussian elimination.

        :param matrix: A Matrix object to triangularize.
        :return: A new Matrix object in lower triangular form.
        """
        rows = matrix.rows
        m = matrix.m

        for p in range(m):
            Matrix.pivoting(matrix, m, p)
            for i in range(p + 1, m):
                factor = rows[i].coords[p] / rows[p].coords[p]
                rows[i] = rows[i] - (rows[p] * factor)
        
        return Matrix(rows)
    
        
    def pivoting(matrix, m, p):
        """
        Performs row pivoting on a matrix to maximize the pivot element in a given column.

        :param matrix: A Matrix object.
        :param m: The number of rows in the matrix.
        :param p: The current pivot column index.
        :return: A new Matrix object with the rows pivoted.
        """

        tmp = []
        a = []
        b = []

        for row in matrix.rows:
            a.append(row.coords)

        max_row = p
        
        for i in range(p, m):
            if abs(a[i][p]) > abs(a[max_row][p]):
                max_row = i

        if (max_row != p):
            tmp = a[p] 
            a[p] = a[max_row]
            a[max_row] = tmp
        
        for row in a:
            b.append(Vector(row))

        return Matrix(b)

    
    def back(matrix):
        """
        Performs back substitution on an upper triangular matrix to solve a system of linear equations.

        :param matrix: A Matrix object in upper triangular form.
        :return: A list of solutions to the linear system, or None if the matrix is singular.
        """
        rows = []
        for vector in matrix.rows:
            rows.append(vector.coords)

        m = matrix.m
        n = matrix.n
        x = []
        
        for i in range(n -1):
            x.append(0)

        try:
            x[m - 1] = rows[m - 1][n - 1] / rows[m - 1][n - 2]

            for i in range(m - 2, -1, -1): # start from the second last row upto 0
                x[i] = rows[i][n - 1]
                for j in range(i + 1, n - 1):
                    x[i] = x[i] - rows[i][j] * x[j]

                x[i] = x[i]/rows[i][i]
        except ZeroDivisionError:
            return None
        return x

