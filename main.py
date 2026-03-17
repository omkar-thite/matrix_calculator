import tkinter as tk
from tkinter import ttk, messagebox, font
from functools import partial
from vector import Vector, Matrix
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
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 2. Calculate 50% of the screen size (must be converted to integers)
        window_width = int(screen_width * 0.25)
        window_height = int(screen_height * 0.25)

        # 3. Apply the dimensions to the window
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(700, 500)
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

    def ensure_window_for_matrices(self, rows, cols, matrix_count=1):
        """Grow the window to fit matrix-heavy screens while staying within display bounds."""
        matrix_count = max(1, int(matrix_count))
        rows = max(1, int(rows))
        cols = max(1, int(cols))

        estimated_width = (cols * 90) + 360
        estimated_height = (rows * 46 * matrix_count) + 320

        max_width = max(700, self.screen_width - 120)
        max_height = max(500, self.screen_height - 140)

        width = min(max_width, max(700, estimated_width))
        height = min(max_height, max(500, estimated_height))
        self.root.geometry(f"{width}x{height}")


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


class MatrixOperationFrameBase(OperationFrameBase):
    def __init__(self, parent, controller, title):
        super().__init__(parent, controller, title, MatrixHomeFrame)

        outer_body = self.body
        outer_body.columnconfigure(0, weight=1)
        outer_body.rowconfigure(0, weight=1)

        self._scroll_canvas = tk.Canvas(outer_body, highlightthickness=0)
        self._v_scroll = ttk.Scrollbar(
            outer_body, orient="vertical", command=self._scroll_canvas.yview
        )
        self._h_scroll = ttk.Scrollbar(
            outer_body, orient="horizontal", command=self._scroll_canvas.xview
        )

        self._scroll_canvas.configure(
            yscrollcommand=self._v_scroll.set,
            xscrollcommand=self._h_scroll.set,
        )

        self._scroll_canvas.grid(column=0, row=0, sticky="nsew")
        self._v_scroll.grid(column=1, row=0, sticky="ns")
        self._h_scroll.grid(column=0, row=1, sticky="ew")

        self.body = ttk.Frame(self._scroll_canvas)
        self.body.columnconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=1)

        self._scroll_window = self._scroll_canvas.create_window(
            (0, 0), window=self.body, anchor="nw"
        )

        self.body.bind("<Configure>", self._on_scroll_content_configure)
        self._scroll_canvas.bind("<Configure>", self._on_scroll_canvas_configure)
        self._scroll_canvas.bind("<Button-4>", self._on_mousewheel_up)
        self._scroll_canvas.bind("<Button-5>", self._on_mousewheel_down)

    def _on_scroll_content_configure(self, _event):
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_scroll_canvas_configure(self, event):
        current_width = self._scroll_canvas.itemcget(self._scroll_window, "width")
        if not current_width:
            self._scroll_canvas.itemconfigure(self._scroll_window, width=event.width)

    def _on_mousewheel_up(self, _event):
        self._scroll_canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, _event):
        self._scroll_canvas.yview_scroll(1, "units")

    def show_input_step(self):
        raise NotImplementedError

    def clear_body(self):
        super().clear_body()
        self._scroll_canvas.yview_moveto(0)
        self._scroll_canvas.xview_moveto(0)

    def create_matrix_grid(self, start_row, rows, cols, label):
        ttk.Label(self.body, text=label, font=self.custom_font).grid(
            column=0, row=start_row, columnspan=2, sticky=W, pady=(8, 4)
        )

        frame = ttk.Frame(self.body)
        frame.grid(column=0, row=start_row + 1, columnspan=2, sticky=W, pady=(0, 8))

        entries = []
        for i in range(rows):
            row_entries = []
            for j in range(cols):
                entry = ttk.Entry(frame, width=8)
                entry.grid(row=i, column=j, padx=4, pady=4)
                row_entries.append(entry)
            entries.append(row_entries)

        return entries, start_row + 2

    def flatten_entries(self, matrix_entry_sets):
        flattened = []
        for matrix_entries in matrix_entry_sets:
            for row_entries in matrix_entries:
                flattened.extend(row_entries)
        return flattened

    def show_matrix_result(self, matrix, heading="Resultant matrix:"):
        self.clear_body()
        ttk.Label(self.body, text=heading, font=self.custom_font).grid(
            column=0, row=0, columnspan=2, sticky=W, pady=(0, 10)
        )

        frame = ttk.Frame(self.body)
        frame.grid(column=0, row=1, columnspan=2, sticky=W)

        for i, vector in enumerate(matrix.rows):
            for j, value in enumerate(vector.coords):
                ttk.Label(frame, text=str(value), padding=5).grid(row=i, column=j, padx=3, pady=3)

        ttk.Button(self.body, text="Try Again", command=self.show_input_step).grid(
            column=1, row=2, sticky=E, pady=(12, 0)
        )


class MatrixAddSubtractOpFrame(MatrixOperationFrameBase):
    operation = ADD
    title = "Matrix Addition"

    def __init__(self, parent, controller):
        super().__init__(parent, controller, self.title)
        self.matrix_entries = []
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()
        action = "add" if self.operation == ADD else "subtract"

        ttk.Label(self.body, text=f"Number of matrices to {action}:", font=self.custom_font).grid(
            column=0, row=0, sticky=W, pady=(0, 8)
        )
        count_entry = ttk.Entry(self.body, width=12)
        count_entry.grid(column=1, row=0, sticky=E, pady=(0, 8))

        ttk.Label(self.body, text="Dimensions (rows cols):", font=self.custom_font).grid(
            column=0, row=1, sticky=W
        )
        dim_entry = ttk.Entry(self.body, width=12)
        dim_entry.grid(column=1, row=1, sticky=E)

        count_entry.focus_set()
        self.bind_enter_chain([count_entry, dim_entry], lambda: self.show_matrices_step(count_entry, dim_entry))

        ttk.Button(
            self.body,
            text="Next",
            command=lambda: self.show_matrices_step(count_entry, dim_entry),
        ).grid(column=1, row=2, sticky=E, pady=(12, 0))

    def show_matrices_step(self, count_entry, dim_entry):
        try:
            count = int(count_entry.get())
            if count < 2:
                raise ValueError
            rows, cols = parse_dimensions_text(dim_entry.get())
        except ValueError as error:
            self.show_error(str(error) if str(error) else "Enter valid count and dimensions.")
            return

        self.controller.ensure_window_for_matrices(rows, cols, count)

        self.clear_body()
        self.matrix_entries = []
        row_cursor = 0

        for i in range(1, count + 1):
            entries, row_cursor = self.create_matrix_grid(row_cursor, rows, cols, f"Matrix {i}")
            self.matrix_entries.append(entries)

        all_entries = self.flatten_entries(self.matrix_entries)
        if all_entries:
            all_entries[0].focus_set()
            self.bind_enter_chain(all_entries, self.calculate_result)

        ttk.Button(self.body, text="Calculate", command=self.calculate_result).grid(
            column=1, row=row_cursor, sticky=E, pady=(12, 0)
        )

    def calculate_result(self):
        try:
            matrices = []
            for matrix_entries in self.matrix_entries:
                cells = [[entry.get() for entry in row] for row in matrix_entries]
                matrices.append(parse_matrix_from_cells(cells))
            result = matrix_add_subtract(matrices, self.operation)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_matrix_result(result)


class MatrixAdditionOpFrame(MatrixAddSubtractOpFrame):
    operation = ADD
    title = "Matrix Addition"


class MatrixSubtractionOpFrame(MatrixAddSubtractOpFrame):
    operation = SUBTRACT
    title = "Matrix Subtraction"


class MatrixScalarOpFrame(MatrixOperationFrameBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Matrix Scalar Multiplication")
        self.matrix_entries = []
        self.scalar_value = 0.0
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()
        ttk.Label(self.body, text="Scalar:", font=self.custom_font).grid(column=0, row=0, sticky=W)
        scalar_entry = ttk.Entry(self.body, width=12)
        scalar_entry.grid(column=1, row=0, sticky=E)

        ttk.Label(self.body, text="Dimensions (rows cols):", font=self.custom_font).grid(
            column=0, row=1, sticky=W, pady=(8, 0)
        )
        dim_entry = ttk.Entry(self.body, width=12)
        dim_entry.grid(column=1, row=1, sticky=E, pady=(8, 0))

        scalar_entry.focus_set()
        self.bind_enter_chain([scalar_entry, dim_entry], lambda: self.show_matrix_step(scalar_entry, dim_entry))

        ttk.Button(
            self.body,
            text="Next",
            command=lambda: self.show_matrix_step(scalar_entry, dim_entry),
        ).grid(column=1, row=2, sticky=E, pady=(12, 0))

    def show_matrix_step(self, scalar_entry, dim_entry):
        try:
            self.scalar_value = parse_scalar_text(scalar_entry.get())
            rows, cols = parse_dimensions_text(dim_entry.get())
        except ValueError as error:
            self.show_error(str(error))
            return

        self.controller.ensure_window_for_matrices(rows, cols, 1)

        self.clear_body()
        matrix_entries, row_cursor = self.create_matrix_grid(0, rows, cols, "Matrix")
        self.matrix_entries = [matrix_entries]

        all_entries = self.flatten_entries(self.matrix_entries)
        if all_entries:
            all_entries[0].focus_set()
            self.bind_enter_chain(all_entries, self.calculate_result)

        ttk.Button(self.body, text="Calculate", command=self.calculate_result).grid(
            column=1, row=row_cursor, sticky=E, pady=(12, 0)
        )

    def calculate_result(self):
        try:
            cells = [[entry.get() for entry in row] for row in self.matrix_entries[0]]
            matrix = parse_matrix_from_cells(cells)
            result = matrix_scalar_multiply(matrix, self.scalar_value)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_matrix_result(result)


class MatrixMultiplyOpFrame(MatrixOperationFrameBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Matrix Multiplication")
        self.matrix_entries = []
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()
        ttk.Label(self.body, text="Matrix 1 dimensions (rows cols):", font=self.custom_font).grid(
            column=0, row=0, sticky=W
        )
        dim1_entry = ttk.Entry(self.body, width=12)
        dim1_entry.grid(column=1, row=0, sticky=E)

        ttk.Label(self.body, text="Matrix 2 dimensions (rows cols):", font=self.custom_font).grid(
            column=0, row=1, sticky=W, pady=(8, 0)
        )
        dim2_entry = ttk.Entry(self.body, width=12)
        dim2_entry.grid(column=1, row=1, sticky=E, pady=(8, 0))

        dim1_entry.focus_set()
        self.bind_enter_chain([dim1_entry, dim2_entry], lambda: self.show_matrices_step(dim1_entry, dim2_entry))

        ttk.Button(
            self.body,
            text="Next",
            command=lambda: self.show_matrices_step(dim1_entry, dim2_entry),
        ).grid(column=1, row=2, sticky=E, pady=(12, 0))

    def show_matrices_step(self, dim1_entry, dim2_entry):
        try:
            r1, c1 = parse_dimensions_text(dim1_entry.get())
            r2, c2 = parse_dimensions_text(dim2_entry.get())
            if c1 != r2:
                raise ValueError("Matrix dimensions are not valid for multiplication.")
        except ValueError as error:
            self.show_error(str(error))
            return

        self.controller.ensure_window_for_matrices(max(r1, r2), max(c1, c2), 2)

        self.clear_body()
        m1_entries, row_cursor = self.create_matrix_grid(0, r1, c1, "Matrix 1")
        m2_entries, row_cursor = self.create_matrix_grid(row_cursor, r2, c2, "Matrix 2")
        self.matrix_entries = [m1_entries, m2_entries]

        all_entries = self.flatten_entries(self.matrix_entries)
        if all_entries:
            all_entries[0].focus_set()
            self.bind_enter_chain(all_entries, self.calculate_result)

        ttk.Button(self.body, text="Calculate", command=self.calculate_result).grid(
            column=1, row=row_cursor, sticky=E, pady=(12, 0)
        )

    def calculate_result(self):
        try:
            first_cells = [[entry.get() for entry in row] for row in self.matrix_entries[0]]
            second_cells = [[entry.get() for entry in row] for row in self.matrix_entries[1]]
            matrix_a = parse_matrix_from_cells(first_cells)
            matrix_b = parse_matrix_from_cells(second_cells)
            result = matrix_multiply(matrix_a, matrix_b)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_matrix_result(result)


class MatrixTransformOpFrame(MatrixOperationFrameBase):
    operation = "transpose"
    title = "Transpose"

    def __init__(self, parent, controller):
        super().__init__(parent, controller, self.title)
        self.matrix_entries = []
        self.show_input_step()

    def show_input_step(self):
        self.clear_body()
        ttk.Label(self.body, text="Dimensions (rows cols):", font=self.custom_font).grid(
            column=0, row=0, sticky=W
        )
        dim_entry = ttk.Entry(self.body, width=12)
        dim_entry.grid(column=1, row=0, sticky=E)
        dim_entry.focus_set()

        ttk.Button(
            self.body,
            text="Next",
            command=lambda: self.show_matrix_step(dim_entry),
        ).grid(column=1, row=1, sticky=E, pady=(12, 0))
        dim_entry.bind("<Return>", lambda event: self.show_matrix_step(dim_entry))

    def show_matrix_step(self, dim_entry):
        try:
            rows, cols = parse_dimensions_text(dim_entry.get())
        except ValueError as error:
            self.show_error(str(error))
            return

        self.controller.ensure_window_for_matrices(rows, cols, 1)

        self.clear_body()
        entries, row_cursor = self.create_matrix_grid(0, rows, cols, "Matrix")
        self.matrix_entries = [entries]

        all_entries = self.flatten_entries(self.matrix_entries)
        if all_entries:
            all_entries[0].focus_set()
            self.bind_enter_chain(all_entries, self.calculate_result)

        ttk.Button(self.body, text="Calculate", command=self.calculate_result).grid(
            column=1, row=row_cursor, sticky=E, pady=(12, 0)
        )

    def calculate_result(self):
        try:
            cells = [[entry.get() for entry in row] for row in self.matrix_entries[0]]
            matrix = parse_matrix_from_cells(cells)

            if self.operation == "transpose":
                result = matrix_transpose(matrix)
            else:
                result = matrix_gaussian_elimination(matrix)
        except ValueError as error:
            self.show_error(str(error))
            return

        self.show_matrix_result(result)


class MatrixTransposeOpFrame(MatrixTransformOpFrame):
    operation = "transpose"
    title = "Transpose"


class MatrixGaussianOpFrame(MatrixTransformOpFrame):
    operation = "gauss"
    title = "Gaussian Elimination"


class MatrixHomeFrame(GenericMenuFrame):
    # Supported operations dictionary for GUI buttons
    matrix_ops = {
                    "Addition": MatrixAdditionOpFrame,
                    "Subtraction": MatrixSubtractionOpFrame,
                    "Multiplication": MatrixMultiplyOpFrame,
                    "Scalar Multiplication": MatrixScalarOpFrame,
                    "Transpose": MatrixTransposeOpFrame,
                    "Gaussian Elimination": MatrixGaussianOpFrame,
                   }

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Select Matrix Operation", self.matrix_ops, HomeFrame)



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

