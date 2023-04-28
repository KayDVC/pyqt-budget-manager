from PyQt6.QtWidgets import QWidget, QMainWindow, QGridLayout, QHBoxLayout, \
                          QTableWidget, QPushButton, QScrollArea, QTableWidgetItem, \
                          QComboBox, QLineEdit, QLabel, \
                          QAbstractItemView, QHeaderView
from PyQt6.QtCharts import QPieSeries, QChart, QChartView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPainter
from expense_report import Category
from expense_operations import Operation, OperationWindow


class ExpenseManagerUI(QMainWindow):
    """ Creates and displays Revenue and Expenses in user interface.
    
    Contains functions for creating graphical user interface (popup window) and displaying pertinent budget
    information. Required functionality includes category filtering, revenue/expense/transfer operations, and
    budget visualization using a pie chart.
    
    Utilizes the PyQt6 library to create, format, and display GUI.

    Attributes:
        main_widget: QWidget object to house all other objects displayed. 
        main_layout: a QGridLayout object to house children elements.
        categories: a dictionary of category names and objects to start UI with.
        operation_bar: a QHBoxLayout object to house all widgets to fullfil
                       assigned operations.
        category_table: a dictionary containing a QGridLayout object and a nested dictionary
                        containing the widgets within the layout.
                        Dictionary items: 
                            "layout", "components: 'filter_box','data_table', 'total_line' "
        expense_chart: a QChartView object the necessary objects needed to diplay a 
                       pie chart of all expenses.
        popup : A QWidget object that serves as a secondary pop-up window for
                operations and operation results.
    """

    # Describe layout spans
    HALF_COLUMN, FULL_COLUMN  = 1, 2
    FULL_ROW = 1

    def __init__(self, categories: list[Category]):
        super(ExpenseManagerUI, self).__init__(None)
        self._main_widget = None
        self._main_layout = None
        self._categories = self._createCategories(categories)
        self._operation_bar = None
        self._category_table = {}
        self._expense_chart = None
        self._popup = None

        self._setup_window()
        self._layout_ui()
        self.show()

    def _createCategories(self, categories: list[Category]) -> dict[str, Category]:
        """Create and return populated category dictionary.

        Args:
            categories: a list of Category objects to populate the dictionary with.

        Returns:
            A dictionary with category names as keys and objects as values based on passed
            list.
        """
        category_dict = {}
        for category in categories:
            category_dict[category.category] = category

        return category_dict
            
    def _setup_window(self) :
        """Creates UI window and sets window title. 
        """
        width = 800
        height = 400

        # set window dimensions & title.
        self.setWindowTitle("Budget Manager")
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setContentsMargins(0,0,0,0)
        self.menuBar().hide()
        self.statusBar().hide()
    
    def _layout_ui(self):
        """Instantiates and runs creation functions for all widgets/sub layouts in main layout.

        """

        # create, configure, and set main widget.
        self._main_widget = QWidget(self)
        self._main_widget.setContentsMargins(0,40,0,40)
        self.setCentralWidget(self._main_widget)

        # create and configure window layout.
        self._main_layout = QGridLayout()
        self._main_layout.setContentsMargins(40, 0, 40, 0)
        self._main_layout.setVerticalSpacing(0)
        for col in range(2):
            self._main_layout.setColumnMinimumWidth(col, 360)
        
        # create UI elements and add to layout.
        self._operation_bar = self._create_operation_bar()

        self._category_table["components"] = {"filter_box": None, "data_table": None, "total_line": None}
        self._category_table["layout"] = self._make_category_table()
        self._expense_chart = self._make_expense_chart()

        # add pre-built layouts
        self._main_layout.addLayout(self._operation_bar, 0, 0, self.FULL_ROW, self.FULL_COLUMN)
        self._main_layout.addLayout(self._category_table["layout"], 1, 0, self.FULL_ROW, self.HALF_COLUMN)
        self._main_layout.addWidget(self._expense_chart, 1, 1, self.FULL_ROW, self.HALF_COLUMN)

        # add layout to window.
        self._main_widget.setLayout(self._main_layout)


    ## --------------------------------------------
    ## Budget Operation Functions 
    ## --------------------------------------------
    def _create_operation_bar(self) -> QHBoxLayout:
        """Create and return styled and configured operation buttons.

        Returns:
            A QHBoxLayout containing configured buttons that open various popup windows
            when clicked.
        """

        operation_bar = QHBoxLayout()

        buttons = { "category": [QPushButton("Add Category"), lambda: self._operation_popup(Operation.AddCategory)],
                    "revenue": [QPushButton("Add Revenue"), lambda: self._operation_popup(Operation.AddRevenue)],
                    "expense": [QPushButton("Add Expense"), lambda: self._operation_popup(Operation.AddExpense)],
                    "transfer": [QPushButton("Transfer Money"), lambda: self._operation_popup(Operation.TransferMoney)]
                   }
        # set functions for buttons and add to layout
        for button_set in buttons:
            
            button = buttons[button_set][0]
            button_op = buttons[button_set][1]
            button.clicked.connect(button_op)
            operation_bar.addWidget(button, 2, Qt.AlignmentFlag.AlignHCenter)

        return operation_bar

    def _operation_popup(self, operation: Operation):
        """ Create popup window based on desired operation.

        Args:
            operation: an Operation enum representing the desired user funtionality.

        Note: 
            Opens a popup which takes control over main app. Main window's input will be 
            disabled until the popup is closed.
        """
        self._popup = OperationWindow(operation, self._categories)
        self._popup.show()

        # prevent completion of code block until popup window closed.
        self._popup.exec()

        # update category objects from operation
        self._categories = self._popup.getCategories()

        # update data table without changing current filter.
        self._update_data_table(self._category_table["components"]["filter_box"].currentText())
        # update pie chart with all expenses.
        self._update_expense_chart()


    ## --------------------------------------------
    ## Category Table Functions 
    ## --------------------------------------------

    def _make_category_table(self) -> QGridLayout:
        """Instantiates and runs creation functions for all widgets necessary to display category information.

        Returns:
            A QGridLayout containing selectable categories and their accompanying information.
        """

        # create and configure layout
        category_table = QGridLayout()
        category_table.setSpacing(20)

        # create category filter and add available categories
        filter_box = QComboBox()
        filter_box.addItems([category for category in self._categories])
        filter_box.setCurrentIndex(0)
        filter_box.currentIndexChanged.connect(lambda: self._update_data_table(filter_box.currentText()))
        self._category_table["components"]["filter_box"] = filter_box

        data_table = self._make_data_table(filter_box.currentText())
        self._category_table["components"]["data_table"] = data_table

        # create and configure layout to display total.
        total_area = QHBoxLayout()
        
        total_label = QLabel()  # not worth making accessible outside this function; non-changing data.
        total_label.setText("TOTAL")

        total_line = QLineEdit()
        total_line.setReadOnly(True) # user should not be able to change computed value
        total_line.setText(self._compute_category_total(filter_box.currentText()))
        self._category_table["components"]["total_line"] = total_line
        
        total_area.addWidget(total_label, 1)
        total_area.addStretch(1)
        total_area.addWidget(total_line)

        # add widgets and layouts to parent layout
        category_table.addWidget(filter_box, 0, 0)
        category_table.addWidget(data_table, 1, 0)
        category_table.addLayout(total_area, 2, 0)
    
        return category_table
    
        
    def _update_data_table(self, category_name: str):
        """Recreates display with new category data and updates category selections.

        Args:
            category_name: the name of the category object to get data from.
        """
        
        # remove widget
        self._category_table["layout"].removeWidget(
            self._category_table["components"]["data_table"])
        
        # recreate widget
        self._category_table["components"]["data_table"] = self._make_data_table(category_name)

        # add to layout
        self._category_table["layout"].addWidget(
            self._category_table["components"]["data_table"], 1, 0
        )

        # update total
        self._category_table["components"]["total_line"].setText(self._compute_category_total(category_name))

        # update category list if necessary
        selection = lambda: self._category_table["components"]["filter_box"]

        not_added = [key for key in self._categories.keys() if key not in 
                     [selection().itemText(i) for i in range(selection().count())]]

        selection().addItems([category for category in not_added])

        


    def _make_data_table(self, category_name: str) -> QScrollArea:
        """Compiles category data in simple, scrollable display.

        Args:
            category_name: the name of the category object to get data from.

        Returns:
            A QScrollArea object containing category transactions and remaining total.
        """

        category_obj = self._categories[category_name]
        row_cnt = len(category_obj.wallet)
        col_cnt = 2

        # create and configure parent scoll area
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)

        # create and fill data table
        table = QTableWidget(scroller)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().hide()
        table.setRowCount(row_cnt)
        table.setColumnCount(col_cnt)
        table.setHorizontalHeaderLabels(["Description", "Amount ($)"])
        table.setMinimumHeight(250)
        

        for index, action in enumerate(category_obj.wallet):
            # get action details
            description = action['description'][0:23]
            amount = round(action['amount'], 2)
            if type(amount) == int:
                amount = str(amount) + '.00'

            # add to table
            table.setItem(index, 0, QTableWidgetItem(f"{description}"))
            table.setItem(index, 1, QTableWidgetItem("{:.2f}".format(amount) if type(amount) == float else f"{amount}")) 

        for row in range(row_cnt):  # set height of individual rows
            table.verticalHeader().setSectionResizeMode(row, QHeaderView.ResizeMode.Stretch)
        for col in range(col_cnt):  # set height of individual columns
            table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        #nest table within scroll area and return
        scroller.setWidget(table)
        return scroller


    def _compute_category_total(self, category_name: str) -> str:
        """Fetches category total and converts to formatted string.

        Args:
            category_name: the name of the category object to get remaining balance from.

        Returns:
            A string containing the unused revenue in a category formatted to 2 decimal points.
        """
        category_obj = self._categories[category_name]

        total = category_obj.get_balance()

        if type(total) == int:
            total = str(total) + ".00"
        else:
            total = "{:.2f}".format(total)

        return total

    ## --------------------------------------------
    ## Expense Chart Functions 
    ## --------------------------------------------

    def _make_expense_chart(self) -> QChartView:
        """Creates a pie chart that visualizes each category's valid expenses.

        Returns:
            A QChartView object containing a pie chart that compares each category's 
            valid expenses to the total amount of valid expenses across all categories.

        Note:
            Transfers are not considered a valid expense. Categories with the name "Income"
            are not included in the pie chart due to the above line of reasoning.
        """
        
        graph_data = QPieSeries()

        # add name and total expense of category to graph. PyQt auto calcs
        # the percentage and relational size of slice base on percentage.
        for category in self._categories:
            if(category == "Income"):
                continue
            cat_obj = self._categories[category]
            graph_data.append(category, round(cat_obj.get_expense_total(), 2))

        # display category name and choose semi-random color.
        for index, category_slice in enumerate(graph_data.slices()):
            category_slice.setLabelVisible(True)
            category_slice.setBrush(QBrush(self._get_color(index)))

        # create and configure chart for display.
        chart = QChart()
        chart.addSeries(graph_data)
        chart.legend().hide()
        chart.setTitle("Spending Breakdown")

        # house chart in widget.
        chart_view = QChartView()
        chart_view.setChart(chart)

        # prevents weird console messages when pointer over graph.
        chart_view.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        return chart_view

    def _get_color(self, random_val: int) -> Qt.GlobalColor:
        """Returns a color enum based on passed value.

        Returns:
            A GlobalColor value that signifies a color to be used when displaying an object.

        Note: 
            Cycles through 14 available colors even if a larger index than 14 is provided.
        """
        colors = {
            0: Qt.GlobalColor.red,
            1: Qt.GlobalColor.green,
            2: Qt.GlobalColor.blue,
            3: Qt.GlobalColor.cyan,
            4: Qt.GlobalColor.magenta,
            5: Qt.GlobalColor.yellow,
            6: Qt.GlobalColor.gray,
            7: Qt.GlobalColor.darkRed,
            8: Qt.GlobalColor.darkGreen,
            9: Qt.GlobalColor.darkBlue,
            10: Qt.GlobalColor.darkCyan,
            11: Qt.GlobalColor.darkMagenta,
            12: Qt.GlobalColor.darkYellow,
            13: Qt.GlobalColor.darkGray,
        }
        return (colors[random_val % len(colors.keys())])
    
    def _update_expense_chart(self):
        """Recreates pie chart with new expense data.

        """
        # remove graph
        self._main_layout.removeWidget(self._expense_chart)
        
        # recreate graph
        self._expense_chart = self._make_expense_chart()

        # add back to layout
        self._main_layout.addWidget(self._expense_chart, 1, 1, self.FULL_ROW, self.HALF_COLUMN)

