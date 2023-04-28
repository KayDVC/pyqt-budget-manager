
from expense_manager_ui import ExpenseManagerUI
import fill_data
from PyQt6.QtWidgets import QApplication
import sys

def main():

    app = QApplication(sys.argv)

    ui = ExpenseManagerUI(fill_data.get_fill_data())
    ui.show()
    
    sys.exit(app.exec())




if __name__ == "__main__":
    main()