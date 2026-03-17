import tkinter as tk
from tkinter import ttk, messagebox, font
from functools import partial
from vector import Vector, Matrix

N = tk.N
W= tk.W
E = tk.E
S = tk.S

HOME = "home"
DOT = "dot"
CROSS = "CROSS"
ADD = "addition"
SUBTRACT = "subtraction"
ANGLE = "get angle"
VECTOR = "vector"
MATRIX = "matrix"
SCALAR = "scalar"


class AppController:

    def __init__(self, root):
        '''
        Initialse variables and display home window
        '''
        # Initialize root UI 

        self.root = root
        self.root.title("Matrix Calculator")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 2. Calculate 50% of the screen size (must be converted to integers)
        window_width = int(screen_width * 0.25)
        window_height = int(screen_height * 0.25)

        # 3. Apply the dimensions to the window
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.custom_font = font.Font(family="Helvetica", size=30, weight="bold")
        self.style = ttk.Style(self.root)
        self.style.configure("BigText.TButton", font=self.custom_font.name)

        # Start at the main menu
        self.current_frame = None
        self.show_home()


    def switch_frame(self, new_frame_class):
        """Destroys current frame and loads a new one."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = new_frame_class(self.root, self)
        self.current_frame.grid(column=0, row=0, sticky='nwes')
    
    def show_home(self):
        self.switch_frame(HomeFrame)


class HomeFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        # Configure grid weights for proper alignment
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)

        # Configure Home window
        ttk.Label(self, 
                  text="Select operation",
                  font=controller.custom_font
                  ).grid(column=0, row=1, sticky='ew', pady=(20, 30))
        
        vector_button = ttk.Button(self, 
                                   text="Vector", 
                                   padding=10,
                                   style="BigText.TButton",
                                   command=lambda: controller.switch_frame(VectorHomeFrame)
                                   )
        vector_button.grid(column=0, row=2, sticky='ew', padx=40, pady=10)
        
        matrix_button = ttk.Button(self,
                                   text="Matrix", 
                                   padding=10,
                                   style="BigText.TButton",
                                   command=lambda: controller.switch_frame(MatrixOps)
                                   )
        matrix_button.grid(column=0, row=3, sticky='ew', padx=40, pady=10)

class GenericMenuFrame(ttk.Frame):
    def __init__(self, parent, controller, title, operations, back_frame):
        super().__init__(parent)
        self.controller = controller

        # Configure grid weights for proper alignment
        for i in range(3):
            self.columnconfigure(i, weight=1)
            
        self.rowconfigure(0, weight=0)  # Back button row
        self.rowconfigure(1, weight=0)  # Title row
        self.rowconfigure(2, weight=1)  # Top spacer
        self.rowconfigure(3, weight=0)  # Buttons start row
        # We will add a bottom spacer dynamically after creating buttons

        # Back Button
        ttk.Button(
            self, 
            text="Back", 
            command=lambda: controller.switch_frame(back_frame), 
            padding=10
        ).grid(row=0, column=0, sticky=W, padx=10, pady=10)        
        
        # Dynamic Title
        ttk.Label(
            self, 
            text=title, 
            font=getattr(controller, 'custom_font', ('Arial', 30))
        ).grid(column=0, row=1, columnspan=3, pady=(10, 20), sticky='ew') 

        # Generate Buttons dynamically with math (no manual row/col tracking needed)
        start_row = 3
        max_cols = 3
        
        for i, (btn_text, target_frame) in enumerate(operations.items()):
            row_idx = start_row + (i // max_cols)
            col_idx = i % max_cols
            
            ttk.Button(
                self, 
                text=btn_text, 
                style="BigText.TButton", 
                # CRITICAL FIX: target=target_frame binds the specific frame to this button's lambda
                command=lambda target=target_frame: controller.switch_frame(target), 
                padding=10
            ).grid(row=row_idx, column=col_idx, sticky='ew', padx=10, pady=10)    

        # Add bottom spacer after the last row of buttons
        self.rowconfigure(start_row + (len(operations) // max_cols) + 1, weight=1)


class VectorHomeFrame(GenericMenuFrame):
    # Supported operations dictionary for GUI buttons
    vector_ops = {
                    "Addition": HomeFrame,
                    "Subtraction": HomeFrame, 
                    "Dot Product": HomeFrame,
                    "Cross Product": HomeFrame,
                    "Angle": HomeFrame, 
                    "Scalar Multiplication": HomeFrame, 
                    "Vector Properties": HomeFrame,
                   }

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Select Vector Operation", self.vector_ops, HomeFrame)
        

class VectorAdditionFrame(ttk.Frame):
    def create_entry(self, n: int, col: int, row: int, width=10) -> tuple:
        '''
        Creates a label and an entry widget for input vector
        Returns tuple of a dict object of placed entries with serial integer numbers as keys and number of last row in grid

        Parameters:
        n = number of entries to make
        col = column to place entry
        row = row number to place entry
        width = width of entry widget
        '''
        input = {}

        for i in range(1, n+1):
            # Place a label
            ttk.Label(self.container, text=f"vector {i}: ", font=self.custom_font).grid(column=col, row=row, pady=15)
            
            vector = ttk.Entry(self.container, width=width)
            input[f"{i}"] = vector
            vector.grid(column=col+1, row=row, pady=10, sticky=W)
            row = row + 1

        return input, row
        
    # takes dictionary of entry widgets in kwargs
    # returns list of extracted Vector(s)
    def entry_to_vectors(self, **kwargs) -> list:
        '''
        Converts entry widgets input to Vector objects

        Parameters:
        kwargs = expected a dictionary of entry widgets

        '''
        # number of vectors, n, is passed from previous function call
        tmp = [value for _, value in kwargs.items()]
        
        try:
            vectors = [text_vector.strip().split(" ") for text_vector in tmp]
            total_vectors = len(vectors)
            
            # Converts str values to int
            for i in range(total_vectors):
                vector_length = len(vectors[i])

                for j in range(vector_length):
                    vectors[i][j] = int(vectors[i][j])
            
        #IndexError if dim of vectors not same
        except (IndexError, ValueError):
            messagebox.showerror("Error 3", "Invalid input. error_code=3")
            return
        
        else: 
            vectors = [Vector(vector) for vector in vectors]
       
        return vectors
    
    # Vector addition function gui thread
    def vector_add_gui_1(self, operation=ADD):
        self.new_window()

        if operation == ADD:
            ttk.Label(self.container, text="Number of vectors to add: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15) 

        elif operation == SUBTRACT:
            ttk.Label(self.container, text="Number of vectors to subtract: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15) 

        ttk.Button(self.container, text="Back", command=lambda: self.back(prev="vector")).grid(column=0, row=0, sticky= W, pady=(0, 50))
       
        number = ttk.Entry(self.container)
        number.grid(column=0, row=3, pady=10)
        # Set cursor on entry
        number.focus_set()

        # bind Enter key to entry
        number.bind('<Return>', lambda event: self.vector_add_gui_2(number.get(), operation))

        enter = ttk.Button(self.container, text="Enter", command= lambda event: self.vector_add_gui_2(number.get()))
        enter.grid(column=1, row=3, padx=15, sticky= W)


    # stores input vectors
    def vector_add_gui_2(self, n, operation):
        self.new_window()

        # Dictionary to store Entry widgets
        input = {}

        self.create_button("Back", partial(self.vector_add_gui_1, operation), 0, 0, W)
        ttk.Label(self.container, text="Enter components separated by blankspace: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15)
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=1, row=0, sticky=E)

        try:
            n = int(n)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer. error_code=2")
            self.back(prev="vector")

        else:
            input, last_row = self.create_entry(n, 0, 3)
            
            # Focus cursor on first entry widget    
            input["1"].focus_set()

            # press Enter for next entry
            for j in range(1, n + 1):
                if j < n:
                    input[f"{j}"].bind('<Return>', lambda event, j=j : input[f"{j+1}"].focus_set())
                else:
                    input[f"{j}"].bind('<Return>', lambda event : self.vector_add_gui_3(n, operation, **{key : input[key].get() for key in input}))

        # create dictionary which has all vectors and pass it to same addition function
        ttk.Button(self.container, text="Enter", command=lambda : self.vector_add_gui_3(n, operation, **{key : input[key].get() for key in input})).grid(column=1, row=5+last_row, padx=25, sticky= E)
        

    def vector_add_gui_3(self, n, operation, **kwargs):
        self.new_window()

        ttk.Button(self.container, text="Back", command=lambda: self.vector_add_gui_2(n=n).grid(column=0, row=0, sticky= W))
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=1, row=0, sticky=E)

        # number of vectors, n, is passed from previous function call
        tmp = [value for _, value in kwargs.item()]
        
        try:
            vectors = [vector.strip().split(" ") for vector in tmp]
            vector_length = len(vectors[0])

            for i in range(len(vectors)):
                
                if len(vectors[i]) != vector_length:
                    raise ValueError("Cannot add vectors of different length!")
                
            vectors = [[int(element) for element in vector] for vector in vectors]
         
        except ValueError:
            messagebox.showerror("Error 3", "Invalid input. error_code=3")
            self.vector_add_gui_2(n, operation)
        
        else: 
            vectors = [Vector(vector) for vector in vectors]
         
            sum = vectors[0]
            if operation == ADD:
                for vector in vectors[1:]:
                    sum += vector
                    
            elif operation == SUBTRACT:
                for vector in vectors[1:]:
                    sum -=  vector

            self.show_result_vector(sum, n, operation)             
    # Display resultant vector 
    def show_result_vector(self, vector, n, operation):
        back = self.create_button("Back", partial(self.vector_add_gui_2, n, operation), 0,0, W)
        back.focus_set()
        back.bind('<BackSpace>', lambda event: self.vector_add_gui_2(n, operation))

        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=1, row=0, sticky=E)
        
        result = "["
        
        for i in vector.cords:
            result += f" {str(i)}"

        result += " ]"

        ttk.Label(self.container, text="Resultant Vector: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15) 
        ttk.Label(self.container, text=result, font=self.custom_font).grid(column=2, row=2, columnspan=2, pady=15) 

        
    # Subtraction operation borrows from addition operation
    def vector_subtract(self):
        self.vector_add_gui_1(operation=SUBTRACT)
    
    # Dot, Cross product and get angle implementation
    # Implements GUI logic
    def product(self, operation=""):
        self.new_window()

        col = 0
        row = 0
        n = 2
        self.create_button("Back", partial(self.__init__, self), col, row, W)
        if operation==CROSS:
            ttk.Label(self.container, text="Enter only 3 components separated by blankspace: ", font=self.custom_font).grid(column=col, row=row + 1, columnspan=2, pady=15)
        else:   
            ttk.Label(self.container, text="Enter components separated by blankspace: ", font=self.custom_font).grid(column=col, row=row + 1, columnspan=2, pady=15)

        row += 1

        input, last_row = self.create_entry(n, col, row+1)
    
        # Focus cursor on first entry widget    
        input["1"].focus_set()

        # press Enter for next entry
        for j in range(1, n+1):
            if j < 2:
                input[f"{j}"].bind('<Return>', lambda event, j=j : input[f"{j+1}"].focus_set())
            else:
                input[f"{j}"].bind('<Return>', lambda event : self.product_2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row, operation))

        # create dictionary which has all vectors and pass it to same addition function
        ttk.Button(self.container, text="Enter", command=lambda : self.product_2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row, operation)).grid(column=col, row=last_row + 1, padx=25, sticky=E)
        last_row += 1
#############################
    # Implements operations
    def product_2(self, vectors, col, last_row, operation=""):
        
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__, self.app_object))
        home.grid(column=1, row=0, sticky=E)

    # assuming all goes well and vectors list containes 2 vectors
        if vectors:
            try:
                if operation == DOT:
                    result = Vector.dot(vectors[0], vectors[1])
                    ttk.Label(self.container, text="Dot product: ", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 
                    last_row += 1
                elif operation == CROSS:
                    result = Vector.cross(vectors[0], vectors[1])
                    ttk.Label(self.container, text="Cross product: ", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 
                    last_row += 1
                elif operation == ANGLE:
                    result = Vector.get_angle(vectors[0], vectors[1])
                    result = (result * 180) / 3.14
                    ttk.Label(self.container, text="Angle between vectors in degrees is: ", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 
                    last_row += 1
                
                ttk.Label(self.container, text=result, font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 

            except ValueError:
                messagebox.showerror("Invalid Input!", "Invalid input")
        else:
            return
    # Scalar multiplication of vector
    def scalar(self):
        self.new_window()

        col = 0
        row = 0
        n = 1
        self.create_button("Back", partial(self.__init__, self), col, row, W)
        ttk.Label(self.container, text="Enter components separated by blankspace: ", font=self.custom_font).grid(column=col, row=row + 1, columnspan=2, pady=15)

        row += 1

        input, last_row = self.create_entry(n, col, row+1)
        ttk.Label(self.container, text="Enter scalar: ", font=self.custom_font).grid(column=col, row=last_row, pady=15)
        last_row+=1
        
        scalar = ttk.Entry(self.container)
        scalar.grid(column=col+1, row=last_row-1, pady=15)
        input["scalar"] = scalar
        last_row += 1
    
    # Focus cursor on first entry widget    
        input["1"].focus_set()
        input["1"].bind('<Return>', lambda event : input["scalar"].focus_set())
        
        input["scalar"].bind('<Return>', lambda event : self.scalar2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row+1))

        # create dictionary which has all vectors and pass it to same addition function
        ttk.Button(self.container, text="Enter", command=lambda : self.scalar2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row+1)).grid(column=col, row=last_row + 1, padx=25, sticky=E)

        return
    
    # takes a list of vectors
    def scalar2(self, vectors: 'Vector', col: int, last_row: int) -> None:
        '''
        Takes list of two vectors one of which is a scalar (vector with one entry)
        Displays result on app screen

        '''
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=1, row=0, sticky=E)

        try:
            vector = vectors[0]
            scalar = vectors[1].cords[0]
        except (KeyError, TypeError):
            messagebox.showerror("Invalid input!", "Invalid Input")
            return
        try: 
            result = vector * float(scalar)
            ttk.Label(self.container, text="Scalar product: ", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 
            last_row += 1
            ttk.Label(self.container, text=result, font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 

        except ValueError:
                messagebox.showerror("Invalid Input!", "Invalid input")
                return
        else:
            return    
    # General proerties of a vector

    def vector_properties(self):
        '''
        Displays gui for operation
        '''
        self.new_window()

        col = 0
        row = 0
        n = 1
        self.create_button("Back", partial(self.__init__, self), col, row, W)
        ttk.Label(self.container, text="Enter components separated by blankspace: ", font=self.custom_font).grid(column=col, row=row + 1, columnspan=2, pady=15)

        row += 1

        input, last_row = self.create_entry(n, col, row+1)
        input["1"].focus_set()
        input["1"].bind('<Return>', lambda event : self.vector_properties2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row+1))

        ttk.Button(self.container, text="Enter", command=lambda : self.vector_properties2(self.entry_to_vectors(**{key : input[key].get() for key in input}), col, last_row+1)).grid(column=col, row=last_row + 1, padx=25, sticky=E)

    def vector_properties2(self, vectors, col, last_row):
        '''
        Calculates vector properties and displays them
        '''
        self.new_window()
        self.create_button("Back", partial(self.vector_properties), 0, 0, W)
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=1, row=0, sticky=E)

        if not vectors:
            return self.vector_properties()
        
        vector = vectors[0]
        
        ttk.Label(self.container, text="Entered Vector is: ", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W) 
        last_row += 1

        dimension = vector.dim
        theta = vector.get_theta()
        phi = vector.get_phi()

        properties = {"vector": vector, "dimension": dimension, "theta (in rad)": theta, "phi (in rad)": phi}

        for key in properties:
            ttk.Label(self.container, text=f"{key}: {properties[key]}", font=self.custom_font).grid(column=col, row=last_row + 1, columnspan=2, pady=15, sticky=W)
            last_row += 1
            
    # Supported operations dictionary for GUI buttons
    operations = {

                    "Addition": vector_add_gui_1,
                    "Subtraction": vector_subtract, 
                    "Dot Product": partial(product, operation = DOT),
                    "Cross Product": partial(product, operation = CROSS),
                    "Angle": partial(product, operation = ANGLE), 
                    "Scalar Multiplication": scalar, 
                    "Vector Properties": vector_properties,
                   }
    ######
class MatrixOps(AppController):

    def __init__(self, app_object):
        self.app_object = app_object
        self.root = app_object.root
        self.container = app_object.container
        self.new_window()
        self.home_window(MATRIX)

    
    def create_matrix(self, n, rows, columns, col, last_row, islabel=True, label_start=0):
        '''
        Creates given number of matrices with same with same dimensions and their labels, places them on GUI according to args rows and columns.
        
        Returns dict of created matrix objects as values and serial numbers as keys. {1: matrix1, 2: matrix2, ...}
    
        Parameters:
        n (int) : Number of matrices to create
        rows (int) : Number of rows of matrix(s)
        columns (int) : Number of columns of matrix(s)
        col (int) : Current column in grid
        last_row (int) : Current last row of grid
        islabel (bool): Label matrices if True else not.
        label_start (int) : Start labelling matrices from this number

        '''
        matrices = {}

        row = last_row + 1

        # iterate over matrices
        for k in range(1, n+1):
            matrix = []
            
            if islabel == True:
                ttk.Label(self.container, text=f"matrix {k + label_start}: ", font=self.custom_font, padding=10).grid(column=col, row=row, sticky=W)
                row += 1

            mframe = ttk.Frame(self.container)
            mframe.grid(column=col, row=row, pady=5)

            # iterate over rows
            for _ in range(rows):
                place_column = col
                row_entries = []
                matrix.append(row_entries)
                
                # iterate for columns
                for _ in range (columns):
                    current_entry = ttk.Entry(mframe, width=5)
                    current_entry.grid(column=place_column, row=row, padx=15, pady=15)
                    row_entries.append(current_entry)
                    place_column += 1
                row += 1
            matrices[k] = matrix
                
        return matrices, row
    
    # Set focus on succesive matrix entries upon Enter button is pressed
    def focus(self, i, j, k, rows, columns, number_of_matrix, matrices):
        '''
        Sets focus on successive matrix entries when Enter(or tab) is pressed by user
        
        Parameters:
        i (int) = row number of a matrix
        j (int) = column number of a matrix
        k (int) = Matrix's serial number

        rows (int) = Number of rows in  a matrix
        columns (int) = Number of columns in a matrix
        number_of_matrix = total number of matrices
        matrices = Three dimensional list of matrices which are in form of lists

        matrix[k][i][j] gives j'th entry of i'th row of k'th matrix
        '''

        if j != columns - 1:
            matrices[k][i][j + 1].focus_set()
        else:
            if i != rows - 1:
                matrices[k][i + 1][0].focus_set()
            else:
                if k != number_of_matrix:
                    matrices[k + 1][0][0].focus_set()
                else:
                    return                
    def get_matrix_objects(self, number_of_matrix, rows, columns, matrices):
        '''
        Converts list(s) into Matrix(s) objects
        Returns dict where Converted Matrix objects are values and serial number are keys starting from 1 as in {1: Matrix1, 2: Matrix2, ...}

        Parameters:
        number_of_matrix (int) = total number of matrices to convert
        rows (int) = rows of matrix(s)
        columns (int) = columns of matrix(s)
        matrices = list of matrix lists [[[mat1row1], [mat1row2], ...]
                                            [mat2row1], mat2row2],...]
                                            ...]
        '''
        matrix_dict = {}

        for k in range(1, number_of_matrix + 1):
            matrix = []
            for i in range(rows):
                row = []
                
                for j in range(columns):
                    entry = matrices[k][i][j].get()
                    try:
                        entry = float(entry)
                    except ValueError:
                        messagebox.showerror("Invalid Input!", "Invalid input")
                        return None
                    else:
                        row.append(entry)
                
                matrix.append(row)
            matrix_dict[k] = matrix

        for key in matrix_dict:
            vectors_list = []

            for item in matrix_dict[key]:
                vectors_list.append(Vector(item))
            matrix_dict[key] = Matrix(vectors_list)
     
        return matrix_dict
    
    def matrix_add(self, operation=ADD):
        '''
        This thread implemetns Addition and Subtraction operations as both require similar GUI with minor changes
        '''
  
        self.new_window()
        self.create_button("Back", partial(self.__init__, self.app_object), 0, 0, W, pady=5)

        if operation == ADD:
            ttk.Label(self.container, text="Number of matrices to add: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15, sticky=W)
        elif operation == SUBTRACT:
            ttk.Label(self.container, text="Number of matrices to subtract: ", font=self.custom_font).grid(column=0, row=2, columnspan=2, pady=15, sticky=W) 
       
        ttk.Label(self.container, text="Dimension of matrices separated by space: ", font=self.custom_font).grid(column=0, row=4, columnspan=2, pady=15, sticky=W)
    
        number = ttk.Entry(self.container)
        number.grid(column=0, row=3, pady=10, sticky=W)
        # set cursor on entry
        number.focus_set()

        dimensions = ttk.Entry(self.container)
        dimensions.grid(column=0, row=5, padx=15, sticky=W)

        number.bind('<Return>', lambda event: dimensions.focus_set())

        # bind Enter key to entry
        dimensions.bind('<Return>', lambda event: self.matrix_add_gui2(number.get(), dimensions.get().split(" "), operation))

        enter = ttk.Button(self.container, text="Enter", command = lambda event: self.matrix_add_gui2(number.get(), dimensions.get().split(" "), operation))
        enter.grid(column=1, row=6, padx=15, sticky= E)
        return None


    def matrix_add_gui2(self, n, dimensions, operation=ADD):
        
        self.new_window()
        self.create_button("Back", partial(self.matrix_add), 0, 0, W)

        try:
            n = int(n)
            rows, columns = dimensions
            rows = int(rows)
            columns = int(columns)
        except ValueError:
            messagebox.showerror("Inavlid Input", "Invalid Input")
            self.matrix_add(operation)
        else:
            col = 0
            row = 0
            matrices, last_row = self.create_matrix(n, rows, columns, col, row)   
            
            number_of_matrix = len(matrices)

            matrices[1][0][0].focus_set()

            for k in range(1, number_of_matrix + 1):
                for i in range(rows):
                    for j in range(columns):
                        matrices[k][i][j].bind("<Return>", lambda event, i=i,j=j,k=k,rows=rows,columns=columns,number_of_matrix=number_of_matrix: self.focus(i,j,k,rows,columns,number_of_matrix, matrices))
            
        
            enter = ttk.Button(self.container, text="Enter", command = partial(self.matrix_add_gui3, number_of_matrix, rows, columns, matrices, operation))
            enter.grid(column=0, row=last_row+1, padx=15, sticky= E)

            matrices[number_of_matrix][rows - 1][columns - 1].bind("<Return>", lambda event: enter.focus_set())
            enter.bind("<Return>", lambda event: self.matrix_add_gui3(number_of_matrix, rows, columns, matrices, operation))


    def matrix_add_gui3(self, number_of_matrix, rows, columns, matrices,operation=ADD):
        sum = Matrix([])
        matrix = self.get_matrix_objects(number_of_matrix, rows, columns, matrices)
        
        if operation == ADD:
            for key in matrix:
                sum += matrix[key]
        elif operation == SUBTRACT:
            for key in matrix:
                sum -= matrix[key]

        self.show_result(sum, rows, columns)
    
    # Matrix Scalar Product 
    def scalar_product(self):
        self.new_window()
        self.create_button("Back", partial(self.__init__, self.app_object), 0, 0, W, pady=5)
        col = 0
        row = 1
         
        ttk.Label(self.container, text="Scalar: ", font=self.custom_font).grid(column=col, row=row, pady=15, sticky=W)

        scalar = ttk.Entry(self.container)
        scalar.grid(column=col + 1, row=row, sticky=W)
        scalar.focus_set()
        row += 1

        ttk.Label(self.container, text=f"Dimension of matrix separated by space: ", font=self.custom_font).grid(column=col, row=row, columnspan=2, pady=15, sticky=W)
        row += 1

        dimensions= ttk.Entry(self.container)
        dimensions.grid(column=col, row=row, padx=15, sticky=W)
        row += 1

        enter = ttk.Button(self.container, text="Enter", command = partial(self.product_gui2, row + 1))
        enter.grid(column=col + 1, row=row - 1, padx=15, sticky=W)
    
        scalar.bind("<Return>", lambda event : dimensions.focus_set())
        enter.bind("<Return>", lambda event : self.product_gui2(dimensions, row + 1, scalar))

        dimensions.bind("<Return>", lambda event : enter.focus_set())
        
        enter.bind("<Return>", lambda event : self.product_gui2(dimensions.get().strip().split(" "), row + 1, scalar.get().strip()))

      
    def product_gui2(self, dimensions, last_row, scalar):
        # Number of matrices
        n = 1

        try:
            for i in range(n):
                rows, columns = dimensions
                rows = int(rows)
                columns = int(columns)
                scalar = int(scalar)

        except ValueError:
            messagebox.showerror("Inavlid Input", "Invalid Input")
            self.scalar_product()
        else:
            matrix, last_row = self.create_matrix(n, rows, columns, 0, last_row, True)

            matrix[1][0][0].focus()

            for k in range(1, n + 1):
                for i in range(rows):
                    for j in range(columns):
                        matrix[k][i][j].bind("<Return>", lambda event, i=i,j=j,k=k,rows=rows,columns=columns,number_of_matrix=n: self.focus(i,j,k,rows,columns,number_of_matrix, matrix))
            
            enter = ttk.Button(self.container, text="Enter", command = partial(self.product_gui3, matrix, rows, columns, n))
            enter.grid(column=1, row=last_row+1, padx=15, sticky=W)
            last_row = 3

            matrix[n][rows - 1][columns - 1].bind("<Return>", lambda event: enter.focus_set())
            enter.bind("<Return>", lambda event: self.product_gui3(scalar, matrix, rows, columns, n))

    def product_gui3(self, scalar, matrix, rows, columns, n):
        matrix_dict = self.get_matrix_objects(n, rows, columns, matrix)
        result = matrix_dict[1] * scalar
        self.show_result(result, rows, columns)

    # Matrix Multiplication
    def matrix_multiply(self):
        self.new_window()
        self.create_button("Back", partial(self.__init__, self.app_object), 0, 0, W, pady=5)
        col = 0
        row = 1
        # Number of matrices
        n = 2

        # Verify dimensions condition
        dimensions = {}
        for i in range(1, n + 1):
            ttk.Label(self.container, text=f"Dimension of matrix {i} separated by space: ", font=self.custom_font).grid(column=col, row=row, columnspan=2, pady=15, sticky=W)
            row += 1

            dimensions[i] = ttk.Entry(self.container)
            dimensions[i].grid(column=col, row=row, padx=15, sticky=W)
            row += 1
        
        dimensions[1].focus_set()
        dimensions[1].bind("<Return>", lambda event: dimensions[2].focus_set())
        
        enter = ttk.Button(self.container, text="Enter", command = partial(self.matrix_multiply2))
        enter.grid(column=col + 1, row=row - 1, padx=15, sticky=W)
    
        dimensions[2].bind("<Return>", lambda event : enter.focus_set())
        enter.bind("<Return>", lambda event : self.matrix_multiply2(dimensions))

    # Returns dimensions as an int list [rows, columns]
    def extract_dimensions(self, dimensions):
        dim = []

        # Extract dimensions from entries
        try: 
            for key in dimensions:
                rows, columns = dimensions[key].get().strip().split(" ")
                dim.append((int(rows), int(columns)))
        except ValueError:
            messagebox.showerror("Inavlid Input", "Invalid dimensions!")
            return None
                
        return dim
    
    # Verify dimensions and create matrix window
    def matrix_multiply2(self, dimensions):
        dim = self.extract_dimensions(dimensions)

        if dim[0][1] != dim[1][0]:
            messagebox.showerror("Inavlid Input", "Dimensions not suitable for multiplication!")
            self.matrix_multiply()
        else:
            self.new_window()
            self.create_button("Back", partial(self.matrix_multiply), 0, 0, W, pady=5)
            ttk.Label(self.container, text=f"Use tab to go to next entry. ", font=self.custom_font).grid(column=0, row=1, columnspan=2, pady=15, sticky=W)

            col = 0
            row = 2
            # Number of matrices
            n = 2

            m, n = dim[0]
            p, q = dim[1]

            matrix1, first_last_row = self.create_matrix(1, m, n, 0, row, True, 0)
            matrix2, second_last_row = self.create_matrix(1, p, q, 0, first_last_row, True, 1)

            matrix1[1][0][0].focus()
           
            enter = ttk.Button(self.container, text="Enter", command = partial(self.matrix_multiply3, matrix1, matrix2, m, n, p, q))
            enter.grid(column=col, row=second_last_row + 1, padx=15, sticky=W)
        
            enter.bind("<Return>", lambda event : self.matrix_multiply3(matrix1, matrix2, m, n, p, q))
            
    # Multiply two matrices and show resultant matrix
    def matrix_multiply3(self, matrix1, matrix2, m, n, p, q):
        matrix1 = self.get_matrix_objects(1, m, n, matrix1)
        matrix2 = self.get_matrix_objects(1, p, q, matrix2)
        result = matrix1[1] * matrix2[1]

        self.show_result(result, m, q)
    # Transpose Or Gauss eliminate function thread
    def transpose_matrix(self, operation="transpose"):
        '''
        This thread implements Gauss elimination and transpose operations as both require similar GUI
        '''
        self.new_window()
        self.create_button("Back", partial(self.__init__, self.app_object), 0, 0, W, pady=5)

        ttk.Label(self.container, text=f"Dimension of matrix separated by space: ", font=self.custom_font).grid(column=0, row=1, columnspan=2, pady=15, sticky=W)
    
        dimensions= ttk.Entry(self.container)
        dimensions.grid(column=0, row=2, padx=15, sticky=W)
        dimensions.focus_set()
        dimensions.bind("<Return>", lambda event: enter.focus_set())

        enter = ttk.Button(self.container, text="Enter", command = partial(self.transpose2, dimensions, 2, operation))
        enter.grid(column=1, row=2, padx=15, sticky=W)
        end_row = 2

        enter.bind("<Return>", lambda event: self.transpose2(dimensions, end_row, operation))
    
    # Create matrix of given dimensions
    def transpose2(self, dimensions, end_row, operation):
        try:
            rows, columns = dimensions.get().strip().split(" ")
            rows = int(rows)
            columns = int(columns)

        except ValueError:
            messagebox.showerror("Inavlid Input", "Invalid dimensions!")
            self.transpose_matrix()
        else:
            n = 1
            matrix, last_row = self.create_matrix(n, rows, columns, 0, end_row, False)

            matrix[1][0][0].focus()
            for k in range(1, n + 1):
                for i in range(rows):
                    for j in range(columns):
                        matrix[k][i][j].bind("<Return>", lambda event, i=i,j=j,k=k,rows=rows,columns=columns,number_of_matrix=n: self.focus(i,j,k,rows,columns,number_of_matrix, matrix))
            
            enter = ttk.Button(self.container, text="Enter", command = partial(self.transpose3, matrix, rows, columns, dimensions, end_row, operation))
            enter.grid(column=0, row=last_row + 1, padx=15, sticky=W)
            matrix[1][rows - 1][columns - 1].bind("<Return>", lambda event: enter.focus_set())

            enter.bind("<Return>", lambda event: self.transpose3(matrix, rows, columns, dimensions, end_row, operation))

    # Transpose or Gauss eliminate matrix and show result
    def transpose3(self, matrix, rows, columns, dimensions, end_row, operation):
        result = self.get_matrix_objects(1, rows, columns, matrix)

        #  
        if operation == "gauss_eliminate": 
            try:

                # get lower triangularised matrix     
                result = Matrix.triangularise(result[1])
                # back substitue
                result = Matrix.back(result)
                length = len(result)

                if result:
                    result = Matrix([Vector(result)])
                else:
                    raise ValueError

            except ValueError:
                messagebox.showerror("Error", "Invalid input for Gauss elimination process!")
                self.transpose2(dimensions, end_row, operation)
            else:
                self.show_result(result, 1, length)
 
        elif operation == "transpose":
                try:
                    result = result[1].transpose()
                    rows = result.m
                    columns = result.n
                except ValueError:
                    messagebox.showerror("Error", "Error while transposing!")
                    self.transpose2(dimensions, end_row, operation)
                else:
                    self.show_result(result, rows, columns)

    # Display resultant matrix for all operations                    
    def show_result(self, matrix, rows, columns):
        self.new_window()
        
        ttk.Label(self.container, text="Resultant matrix: ", font=self.custom_font).grid(column=0, row=0, columnspan=2, pady=15, sticky=W)
        
        result, last_row = self.create_matrix(1, rows, columns, 1, 0, islabel=False)

        for k in range(1,2):
            for i in range(rows):
                for j in range(columns):
                    result[k][i][j].insert(0, matrix.rows[i].cords[j])
        
        home = ttk.Button(self.container, text="Home", command=partial(self.__init__,self.app_object))
        home.grid(column=0, row=last_row+1, sticky=E)
        home.focus_set()
        home.bind("<Return>", lambda event: self.__init__(self.app_object))
             
    # Supported operations
    operations = {
                "Addition" : partial(matrix_add, operation = ADD) , 
                "Subtraction" :  partial(matrix_add, operation = SUBTRACT),
                "Multiplication":  partial(matrix_multiply), 
                "Scalar Multiplication" :  partial(scalar_product),
                "Transpose":partial(transpose_matrix),
                "Gaussian Elimination": partial(transpose_matrix, operation="gauss_eliminate") ,  
                }
    
def main():
    root = tk.Tk()
    root.resizable(False, False)
    app = AppController(root)
    app.root.mainloop()


# CS50P requirement of 3 functions at level of main()
# Not used in GUI application
def matrix_add(matrix1, matrix2):
    return matrix1 + matrix2

def matrix_subtract(matrix1, matrix2):
    return matrix1 - matrix2

def matrix_scalar_multiplication(matrix, scalar):
    return matrix * scalar
    

if __name__ == "__main__":
    main()

