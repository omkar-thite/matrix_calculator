import tkinter as tk
from tkinter import ttk, messagebox, font
from functools import partial
from vector import Vector, Matrix
from operation_services import (
    compute_vector_binary_operation,
    get_vector_properties,
    parse_scalar_text,
    parse_vector_from_text_line,
    parse_vectors_from_text_lines,
    reduce_vectors,
    scalar_multiply_vector,
)

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
                                   command=lambda: controller.switch_frame(MatrixHomeFrame)
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


class OperationFrameBase(ttk.Frame):
    def __init__(self, parent, controller, title, back_frame):
        super().__init__(parent)
        self.controller = controller
        self.custom_font = getattr(controller, "custom_font", ("Arial", 24))
        self.back_frame = back_frame

        for i in range(3):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Button(
            self,
            text="Back",
            command=lambda: controller.switch_frame(back_frame),
            padding=10,
        ).grid(column=0, row=0, sticky=W, padx=10, pady=10)

        ttk.Button(
            self,
            text="Home",
            command=controller.show_home,
            padding=10,
        ).grid(column=2, row=0, sticky=E, padx=10, pady=10)

        ttk.Label(self, text=title, font=self.custom_font).grid(
            column=0, row=1, columnspan=3, sticky="ew", pady=(10, 20)
        )

        self.body = ttk.Frame(self)
        self.body.grid(column=0, row=2, columnspan=3, sticky="nsew", padx=20, pady=10)
        self.body.columnconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=1)

    def clear_body(self):
        for child in self.body.winfo_children():
            child.destroy()

    def show_error(self, message):
        messagebox.showerror("Invalid Input", message)

    def bind_enter_chain(self, entries, on_submit):
        for i, entry in enumerate(entries):
            if i < len(entries) - 1:
                entry.bind("<Return>", lambda event, idx=i: entries[idx + 1].focus_set())
            else:
                entry.bind("<Return>", lambda event: on_submit())


class VectorAddSubtractFrame(OperationFrameBase):
    operation = ADD
    title = "Vector Addition"

    def __init__(self, parent, controller):
        super().__init__(parent, controller, self.title, VectorHomeFrame)
        self.vector_entries = []
        self.n_vectors = 0
        self.show_count_step()

    def show_count_step(self):
        self.clear_body()

        action = "add" if self.operation == ADD else "subtract"
        ttk.Label(
            self.body,
            text=f"Number of vectors to {action}:",
            font=self.custom_font,
        ).grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 10))

        count_entry = ttk.Entry(self.body, width=12)
        count_entry.grid(column=0, row=1, sticky=W)
        count_entry.focus_set()

        submit = ttk.Button(
            self.body,
            text="Enter",
            command=lambda: self.show_components_step(count_entry.get()),
        )
        submit.grid(column=1, row=1, sticky=E)
        count_entry.bind("<Return>", lambda event: self.show_components_step(count_entry.get()))

    def show_components_step(self, n_text):
        try:
            n = int(n_text)
            if n < 2:
                raise ValueError
        except ValueError:
            self.show_error("Please enter an integer greater than or equal to 2.")
            return

        self.n_vectors = n
        self.vector_entries = []
        self.clear_body()

        ttk.Label(
            self.body,
            text="Enter components separated by spaces:",
            font=self.custom_font,
        ).grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 10))

        for i in range(1, n + 1):
            ttk.Label(self.body, text=f"Vector {i}:").grid(column=0, row=i, sticky=W, pady=6)
            entry = ttk.Entry(self.body, width=30)
            entry.grid(column=1, row=i, sticky=E, pady=6)
            self.vector_entries.append(entry)

        if self.vector_entries:
            self.vector_entries[0].focus_set()
            self.bind_enter_chain(self.vector_entries, self.calculate_result)

        ttk.Button(self.body, text="Calculate", command=self.calculate_result).grid(
            column=1, row=n + 1, sticky=E, pady=(12, 0)
        )

    def parse_vectors(self):
        lines = [entry.get() for entry in self.vector_entries]
        return parse_vectors_from_text_lines(lines)

    def calculate_result(self):
        try:
            vectors = self.parse_vectors()
            result = reduce_vectors(vectors, self.operation)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_result(result)

    def show_result(self, vector):
        self.clear_body()
        coords = " ".join(str(value) for value in vector.coords)

        label = "Resultant Vector:"
        ttk.Label(self.body, text=label, font=self.custom_font).grid(
            column=0, row=0, sticky=W, pady=(0, 10)
        )
        ttk.Label(self.body, text=f"[ {coords} ]", font=self.custom_font).grid(
            column=0, row=1, columnspan=2, sticky=W
        )

        ttk.Button(self.body, text="Try Again", command=self.show_count_step).grid(
            column=1, row=2, sticky=E, pady=(12, 0)
        )


class VectorAdditionOpFrame(VectorAddSubtractFrame):
    operation = ADD
    title = "Vector Addition"


class VectorSubtractionOpFrame(VectorAddSubtractFrame):
    operation = SUBTRACT
    title = "Vector Subtraction"


class VectorBinaryOpFrame(OperationFrameBase):
    operation = "dot"
    title = "Vector Operation"

    def __init__(self, parent, controller):
        super().__init__(parent, controller, self.title, VectorHomeFrame)
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()

        if self.operation == "cross":
            prompt = "Enter two 3D vectors (space-separated):"
        else:
            prompt = "Enter two vectors (space-separated):"

        ttk.Label(self.body, text=prompt, font=self.custom_font).grid(
            column=0, row=0, columnspan=2, sticky=W, pady=(0, 10)
        )

        ttk.Label(self.body, text="Vector 1:").grid(column=0, row=1, sticky=W, pady=6)
        first = ttk.Entry(self.body, width=30)
        first.grid(column=1, row=1, sticky=E, pady=6)

        ttk.Label(self.body, text="Vector 2:").grid(column=0, row=2, sticky=W, pady=6)
        second = ttk.Entry(self.body, width=30)
        second.grid(column=1, row=2, sticky=E, pady=6)

        first.focus_set()
        self.bind_enter_chain([first, second], lambda: self.calculate_result(first, second))

        ttk.Button(
            self.body,
            text="Calculate",
            command=lambda: self.calculate_result(first, second),
        ).grid(column=1, row=3, sticky=E, pady=(12, 0))

    def calculate_result(self, first_entry, second_entry):
        try:
            vectors = parse_vectors_from_text_lines([first_entry.get(), second_entry.get()])
            label, result = compute_vector_binary_operation(vectors[0], vectors[1], self.operation)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_result(label, result)

    def show_result(self, label, result):
        self.clear_body()
        ttk.Label(self.body, text=f"{label}:", font=self.custom_font).grid(
            column=0, row=0, sticky=W, pady=(0, 10)
        )

        if isinstance(result, Vector):
            value = f"[ {' '.join(str(x) for x in result.coords)} ]"
        else:
            value = f"{result}"

        ttk.Label(self.body, text=value, font=self.custom_font).grid(
            column=0, row=1, columnspan=2, sticky=W
        )

        ttk.Button(self.body, text="Try Again", command=self.show_input_step).grid(
            column=1, row=2, sticky=E, pady=(12, 0)
        )


class VectorDotOpFrame(VectorBinaryOpFrame):
    operation = "dot"
    title = "Dot Product"


class VectorCrossOpFrame(VectorBinaryOpFrame):
    operation = "cross"
    title = "Cross Product"


class VectorAngleOpFrame(VectorBinaryOpFrame):
    operation = "angle"
    title = "Angle Between Vectors"


class VectorScalarOpFrame(OperationFrameBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Vector Scalar Multiplication", VectorHomeFrame)
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()

        ttk.Label(self.body, text="Enter vector and scalar:", font=self.custom_font).grid(
            column=0, row=0, columnspan=2, sticky=W, pady=(0, 10)
        )

        ttk.Label(self.body, text="Vector:").grid(column=0, row=1, sticky=W, pady=6)
        vector_entry = ttk.Entry(self.body, width=30)
        vector_entry.grid(column=1, row=1, sticky=E, pady=6)

        ttk.Label(self.body, text="Scalar:").grid(column=0, row=2, sticky=W, pady=6)
        scalar_entry = ttk.Entry(self.body, width=30)
        scalar_entry.grid(column=1, row=2, sticky=E, pady=6)

        vector_entry.focus_set()
        self.bind_enter_chain([vector_entry, scalar_entry], lambda: self.calculate_result(vector_entry, scalar_entry))

        ttk.Button(
            self.body,
            text="Calculate",
            command=lambda: self.calculate_result(vector_entry, scalar_entry),
        ).grid(column=1, row=3, sticky=E, pady=(12, 0))

    def calculate_result(self, vector_entry, scalar_entry):
        try:
            vector = parse_vector_from_text_line(vector_entry.get())
            scalar = parse_scalar_text(scalar_entry.get())
            result = scalar_multiply_vector(vector, scalar)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.clear_body()
        ttk.Label(self.body, text="Scalar product:", font=self.custom_font).grid(
            column=0, row=0, sticky=W, pady=(0, 10)
        )
        ttk.Label(
            self.body,
            text=f"[ {' '.join(str(x) for x in result.coords)} ]",
            font=self.custom_font,
        ).grid(column=0, row=1, columnspan=2, sticky=W)
        ttk.Button(self.body, text="Try Again", command=self.show_input_step).grid(
            column=1, row=2, sticky=E, pady=(12, 0)
        )


class VectorPropertiesOpFrame(OperationFrameBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Vector Properties", VectorHomeFrame)
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()
        ttk.Label(self.body, text="Enter vector:", font=self.custom_font).grid(
            column=0, row=0, columnspan=2, sticky=W, pady=(0, 10)
        )

        entry = ttk.Entry(self.body, width=30)
        entry.grid(column=0, row=1, sticky=W)
        entry.focus_set()

        ttk.Button(
            self.body,
            text="Calculate",
            command=lambda: self.calculate_result(entry),
        ).grid(column=1, row=1, sticky=E)
        entry.bind("<Return>", lambda event: self.calculate_result(entry))

    def calculate_result(self, entry):
        try:
            vector = parse_vector_from_text_line(entry.get())
            properties = get_vector_properties(vector)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.clear_body()
        row = 0
        for key, value in properties.items():
            ttk.Label(self.body, text=f"{key}: {value}", font=self.custom_font).grid(
                column=0, row=row, columnspan=2, sticky=W, pady=5
            )
            row += 1

        ttk.Button(self.body, text="Try Again", command=self.show_input_step).grid(
            column=1, row=row, sticky=E, pady=(12, 0)
        )


class VectorHomeFrame(GenericMenuFrame):
    # Supported operations dictionary for GUI buttons
    vector_ops = {
                    "Addition": VectorAdditionOpFrame,
                    "Subtraction": VectorSubtractionOpFrame, 
                    "Dot Product": VectorDotOpFrame,
                    "Cross Product": VectorCrossOpFrame,
                    "Angle": VectorAngleOpFrame, 
                    "Scalar Multiplication": VectorScalarOpFrame, 
                    "Vector Properties": VectorPropertiesOpFrame,
                   }

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Select Vector Operation", self.vector_ops, HomeFrame)


class MatrixHomeFrame(GenericMenuFrame):
    # Supported operations dictionary for GUI buttons
    matrix_ops = {
                    "Addition": HomeFrame,
                    "Subtraction": HomeFrame, 
                    "Dot Product": HomeFrame,
                    "Cross Product": HomeFrame,
                    "Angle": HomeFrame, 
                    "Scalar Multiplication": HomeFrame, 
                    "Vector Properties": HomeFrame,
                   }

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Select Matrix Operation", self.matrix_ops, HomeFrame)



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

