from PyQt6.QtWidgets import QDialog , QMessageBox, QGridLayout, \
                            QComboBox, QLabel, QLineEdit, QPushButton, \
                            QSizePolicy
from PyQt6.QtCore import Qt, QRect
from expense_report import Category
from enum import Enum

class Operation(Enum):
    AddCategory = "Add Category"
    AddRevenue = "Add Revenue"
    AddExpense = "Add Expense"
    TransferMoney = "Transfer Money"


class Result(Enum):
    Failure = 0
    Success = 1


class OperationWindow(QDialog):
    """
    Contains functions for creating graphical user interface (popup window) and conducting operations on budget.
    Required functionality includes adding categories, revenue/expense/transfer operations, and
    displaying result of operations.
    
    Utilizes the PyQt6 library to create, format, and display GUI.

    Attributes:
        main_layout: a QGridLayout object to house children elements.
        result: a ResultWindow object that will display the result whenever an operation is attempted.
        title: a string to display as the heading of the window.
        operation: an Operation numeration specifying the user's intended action.
        categories: a dictionary of category names and objects to start UI with.
        components: a dictionary containing widget descriptions as keys and the accompanying objects as values.

    Note:
        Disbales user interaction with main window.
    """

    def __init__(self, operation: Operation, categories: dict[str, Category]):
        super(OperationWindow, self).__init__()
        self._main_layout = None
        self._result = None
        self._title = None
        self._operation = operation
        self._categories = categories
        self._components = {}
        self._layout_ui()

    def _layout_ui(self):
        """Instantiates and runs creation functions for all widgets/sub layouts in main layout.

        Note: Created widgets are based on user-specified operation.
        """
        # disable all other windows from taking input.
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # set geometry
        self.setGeometry(QRect(100, 100, 500, 300))

        # create and set main layout
        self._main_layout = QGridLayout()
        self._main_layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(self._main_layout)

        # instantiate and window heading to main layout.
        self._title = QLabel("")
        self._title.setStyleSheet("text-decoration: underline; font-size: 20px;")
        self._title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed);
        self._main_layout.addWidget(self._title, 0, 0, 1, 3, Qt.AlignmentFlag.AlignTop)

        if(self._operation == Operation.AddCategory):
            self._layout_add_category()
        elif(self._operation == Operation.AddRevenue):
            self._layout_add_revenue()
        elif(self._operation == Operation.AddExpense):
            self._layout_add_expense()
        elif(self._operation == Operation.TransferMoney):
            self._layout_transfer_money()

    def _create_combo_box(self, on_change, current_index: int = 0) -> QComboBox:
        """Creates a single-item selection widget containing all of the category names.

        Args:
            on_change: a function to run when the user changes selected category name.
                       Can also be None.
            current_index: the index of the category to set as default; optional.

        Returns:
            A QComboBox object containing the category names that runs a the specified 
            function whenver the user selects a new value. 
        """
        # create category filter and add available categories
        filter_box = QComboBox()
        filter_box.setMinimumWidth(250)
        filter_box.addItems([category for category in self._categories])
        filter_box.setCurrentIndex(0 if len(self._categories) == 1 else current_index)

        if (on_change != None):
            filter_box.currentIndexChanged.connect(on_change)

        return filter_box
    
    def _create_line_edit(self, placeholder: str, enable_button: str = "" , needs_int:bool = True) -> QLineEdit:
        """Creates an interactive widget for users to input data.

        Args:
            placeholder: a string containing the text to display when no data is entered in input area.
            enable_button: a string containing the key of a button to enable/disable when based on user input & additional condition; optional.
            needs_int: a boolean representing if the user should only be allowed to input numeric values; defaults to true.

        Returns:
            A QLineEdit object that enables/disables a button based on certain conditions if specified.

        Note: 
            If needs_int == False, any alphanumeric input will enable the specified button.
        """
        new_input = QLineEdit()
        new_input.setPlaceholderText(placeholder)
        new_input.setMinimumWidth(250)

        # disable specified button when input empty or doesn't meet condition.
        if (len(enable_button) > 0 and (self._components.get(enable_button) != None)):
            button_to_enable = self._components[enable_button]
        
            button_to_enable.setEnabled(False)

            if (needs_int):
                # ensure input is only numbers
                new_input.textChanged.connect(
                    lambda: button_to_enable.setEnabled(True) if 
                    ((len(new_input.text()) > 0)  and (new_input.text().isdigit()) )else
                    button_to_enable.setEnabled(False)  
                )
            else:
                # ensure input is valid
                new_input.textChanged.connect(
                    lambda: button_to_enable.setEnabled(True) if 
                    len(new_input.text()) > 0  else
                    button_to_enable.setEnabled(False)  
                )

        return new_input
    
    def _mutually_exclusive_choice(self, changed_filter: str, other_filter: str):
        """Ensures two combo boxes will never have the same value.

        Args:
            changed_filter: a string containing the name of the combo box which has been last edited by user.
            other_filter: a string containing the name of the combo box that should never have the same 
                          value as the changed filter.

        Note:
            Disables the category selected in changed filter on other filter.
        """

        last_index =  self._components[changed_filter]["last_index"]
        curr_index = self._components[changed_filter]["filter"].currentIndex()
        changed= self._components[changed_filter]
        other= self._components[other_filter]

        # enable previously disabled option on opposing combo box. 
        other["filter"].model().item(
            last_index).setEnabled(True)
        # disable current option on opposing combo box
        other["filter"].model().item(
            curr_index).setEnabled(False)
        # update last value to current value
        changed["last_index"] = curr_index


    """
    A set of functions that creates and adds the widgets necessary to carry out the specified operation.
    Also sets title based on operation.
    """

    def _layout_add_category(self):
        # set geometry
        self.setGeometry(QRect(100, 100, 500, 200))

        # set window heading.
        self._title.setText("Add Category")

        self._components["submit_button"] = QPushButton("Submit")
        self._components["cancel_button"] = QPushButton("Cancel")

        self._components["category_name"] = {"label": QLabel("Category Name"), "input" : self._create_line_edit("Enter category name here", "submit_button", False)}

        # assign functions
        inp = lambda: self._components["category_name"]["input"]
        self._components["submit_button"].clicked.connect(
            lambda: self._show_result(
                self._add_category(inp().text()),
                [inp().text()]
            )
        )
        self._components["cancel_button"].clicked.connect(self.close)


        # add widgets to layout.
        self._main_layout.addWidget(self._components["category_name"]["label"], 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._components["category_name"]["input"], 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        self._main_layout.addWidget(self._components["submit_button"], 2, 2, 1, 1)
        self._main_layout.addWidget(self._components["cancel_button"], 2, 3, 1, 1)

    def _layout_add_revenue(self):

        # set window heading.
        self._title.setText("Add Revenue")

        # create components.        
        self._components["to_select"] = {
            "label": QLabel("To") ,
            "filter" : self._create_combo_box(on_change = None), 
            "last_index": 0
            }

        self._components["submit_button"] = QPushButton("Submit")
        self._components["cancel_button"] = QPushButton("Cancel")

        self._components["amount"] = {"label": QLabel("Amount"), "input" : self._create_line_edit("Enter revenue amount here", "submit_button")}
        self._components["description"] = {"label": QLabel("Description"), "input" : self._create_line_edit("Enter description of the revenue here")}


        # assign functions
        to_category = lambda: self._categories[self._components["to_select"]["filter"].itemText(self._components["to_select"]["filter"].currentIndex())]
        amount = lambda: self._components["amount"]["input"]
        description = lambda: self._components["description"]["input"]
        self._components["submit_button"].clicked.connect(
            lambda: self._show_result(
                to_category().add_revenue(self._convert_float(amount().text()), description().text()),
                [to_category().category, amount().text()]
            )
        )
        self._components["cancel_button"].clicked.connect(self.close)

        # add widgets to layout.
        self._main_layout.addWidget(self._components["to_select"]["label"], 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["to_select"]["filter"], 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )

        self._main_layout.addWidget(self._components["amount"]["label"], 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["amount"]["input"], 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )

        self._main_layout.addWidget(self._components["description"]["label"], 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["description"]["input"], 3, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )
        
        self._main_layout.addWidget(self._components["submit_button"], 4, 2, 1, 1)
        self._main_layout.addWidget(self._components["cancel_button"], 4, 3, 1, 1)

    def _layout_add_expense(self):

        # set window heading.
        self._title.setText("Add Expense")

        # create components.        
        self._components["to_select"] = {
            "label": QLabel("To") ,
            "filter" : self._create_combo_box(on_change = None), 
            "last_index": 0
            }

        self._components["submit_button"] = QPushButton("Submit")
        self._components["cancel_button"] = QPushButton("Cancel")

        self._components["amount"] = {"label": QLabel("Amount"), "input" : self._create_line_edit("Enter revenue amount here", "submit_button")}
        self._components["description"] = {"label": QLabel("Description"), "input" : self._create_line_edit("Enter description of the revenue here")}

        # assign functions
        to_category = lambda: self._categories[self._components["to_select"]["filter"].itemText(self._components["to_select"]["filter"].currentIndex())]
        amount = lambda: self._components["amount"]["input"]
        description = lambda: self._components["description"]["input"]
        self._components["submit_button"].clicked.connect(
            lambda: self._show_result(
                to_category().add_expense(self._convert_float(amount().text()), description().text()),
                [to_category().category, amount().text()]
            )
        )
        self._components["cancel_button"].clicked.connect(self.close)

        # add widgets to layout.
        self._main_layout.addWidget(self._components["to_select"]["label"], 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["to_select"]["filter"], 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )

        self._main_layout.addWidget(self._components["amount"]["label"], 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["amount"]["input"], 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )
        
        self._main_layout.addWidget(self._components["description"]["label"], 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["description"]["input"], 3, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )
        
        self._main_layout.addWidget(self._components["submit_button"], 4, 2, 1, 1)
        self._main_layout.addWidget(self._components["cancel_button"], 4, 3, 1, 1)

    def _layout_transfer_money(self):
        # set window heading.
        self._title.setText("Transfer Money")

        # create components.
        self._components["from_select"] = {
            "label": QLabel("From") , 
            "filter" : self._create_combo_box(on_change = lambda: self._mutually_exclusive_choice("from_select", "to_select")),
            "last_index": 0
            }
        
        self._components["to_select"] = {
            "label": QLabel("To") ,
            "filter" : self._create_combo_box(on_change =lambda: self._mutually_exclusive_choice("to_select", "from_select") , current_index = 1), 
            "last_index": 0 if len(self._categories) == 1 else 1
            }
        self._mutually_exclusive_choice("from_select", "to_select")
        self._mutually_exclusive_choice("to_select", "from_select")

        self._components["submit_button"] = QPushButton("Submit")
        self._components["cancel_button"] = QPushButton("Cancel")

        self._components["amount"] = {"label": QLabel("Amount"), "input" : self._create_line_edit("Enter amount to transfer here", "submit_button")}

        # assign functions
        from_category= lambda: self._categories[self._components["from_select"]["filter"].itemText(self._components["from_select"]["filter"].currentIndex())]
        to_category = lambda: self._categories[self._components["to_select"]["filter"].itemText(self._components["to_select"]["filter"].currentIndex())]
        amount = lambda: self._components["amount"]["input"]
        self._components["submit_button"].clicked.connect(
            lambda: self._show_result(
                from_category().transfer_money(self._convert_float(amount().text()) , to_category()),
                [from_category().category, to_category().category, amount().text()]
            )
        )
        self._components["cancel_button"].clicked.connect(self.close)

        # add widgets to layout.
        self._main_layout.addWidget(self._components["from_select"]["label"], 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["from_select"]["filter"], 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )

        self._main_layout.addWidget(self._components["to_select"]["label"], 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["to_select"]["filter"], 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )

        self._main_layout.addWidget(self._components["amount"]["label"], 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter )
        self._main_layout.addWidget(self._components["amount"]["input"], 3, 1, 1, 2, Qt.AlignmentFlag.AlignCenter )
        
        self._main_layout.addWidget(self._components["submit_button"], 4, 2, 1, 1)
        self._main_layout.addWidget(self._components["cancel_button"], 4, 3, 1, 1)

    def _show_result(self, result: bool, inputs: list[str]):
        """Creates and displays a window of operation result and additional info related to operation.

        Args:
            result: a boolean representing the success or failure of the attempted operation.
            inputs: a list of strings containing the user input in relation to the operation.
                          
        Note:
            Opens another popup window. If operation was sucessful, closing the window will close current
            operation window; if not, the current operation window will remain active.
        """
        title = None
        details = None

        if(self._operation == Operation.AddCategory):
            title = f"Added Category Successfully" if result == Result.Success.value else f"Failed to Add Category"
            details = f"{inputs[0].title()} {'added to categories.' if result == Result.Success.value else 'is already a category. Please enter a name not already in use or click cancel.'}"
        elif(self._operation == Operation.AddRevenue):
            title = f"Added Revenue Successfully"
            details = f"Added ${inputs[1]} in revenue to {inputs[0]}"
        if(self._operation == Operation.AddExpense):
            title = f"Added Expense Successfully" if result == Result.Success.value else f"Failed to Add Expense."
            details = f"Added ${inputs[1]} in expenses to {inputs[0]}" if result == Result.Success.value else f"Insufficient funds in {inputs[0]}. Please try another amount or click cancel."
        if(self._operation == Operation.TransferMoney):
            title = f"Transferred Money Successfully" if result == Result.Success.value else f"Failed to Transfer Money."
            details = f"Transferred ${inputs[2]} from {inputs[0]} to {inputs[1]}" if result == Result.Success.value else f"Insufficient funds in {inputs[1]}. Please try another amount or click cancel."
        
        self._result = ResultWindow(title, details)
        self._result.show()

        if (result == Result.Failure.value):
            if (self._components.get('amount', None) == None ):
                self._components['category_name']['input'].setText("")
            else:
                self._components['amount']['input'].setText("")
        else:
            self.close()

    def _add_category(self, category_name) -> bool:
        """Creates a new Category and adds to category dictionary if category not already in dict.

        Args:
            category_name: a string containing the user-specified name of a new category.

        Returns:
            A boolean representing the result of the attempted operation. True if category name is unique; false otherwise.
        """

        for key in self._categories:
            if(key.lower() == category_name.lower()):
               # category name alreayd used.
               return False

        # add category to list and create new category.
        self._categories[category_name.title()] = Category(category_name.title())
        return True


    def _convert_float(self, text: str) -> float:
        """ Converts a string to float.

        Args:
            text: a string containing a numeric value.

        Returns:
            A float rounded to two decimal places.
        """
        return round(float(text), 2)

    def getCategories(self) -> dict[str, Category]:
        """ Returns the category dictionary contained within the object.

        Returns:
            A dictionary containing category names as keys and the associated category objects as values.
        """
        return self._categories
    

    
class ResultWindow(QMessageBox):
    """Creates and displays Revenue and Expenses in user interface.
    
    Contains functions for creating graphical user interface (popup window) and displaying operation result information.
    
    Utilizes the PyQt6 library to create, format, and display GUI.

    Attributes:
        title: a string to display as the heading of the window.
        details: a string containing more detailed information about the operation and its result.
    """
    def __init__(self, title:str, details:str):
        super(ResultWindow, self).__init__()
        self._title = title
        self._details = details
        self._layout_ui()

    def _layout_ui(self):
        # disable all other windows from taking input.
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.setText(self._title)
        self.setInformativeText(self._details)

        

