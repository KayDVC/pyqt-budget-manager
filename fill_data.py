################################
## This is the driver for the Expense Report
## Solution prepared by Dr. Fitz at Florida Tech.
## Do not copy, store, or reproduce without permission from the author.

## Florida Tech Students in CSE 2050 for Spring 2023
## may use this code as part of their Final Project.
## Do not post this code online in any repository, archival system, 
## or device, and do not distribute, transform, or share with friends or any other entity.
################################
from expense_report import Category

def get_fill_data() -> list[Category]:
    # Define Categories
    income = Category("Income")
    food = Category("Food")
    clothing = Category("Clothing")
    auto = Category("Auto")
    grocery = Category("Grocery")
    savings = Category("Savings")


    # Transactions
    income.add_revenue(5000, "Salary from FIT")
    income.add_expense(488, "Rent")
    income.transfer_money(1000, food)
    income.transfer_money(500, clothing)
    income.transfer_money(200, auto)
    income.transfer_money(500, savings)

    food.add_expense(15.89, "Mangestu Restaurant")
    clothing.add_expense(25.55, "H&M")
    clothing.add_expense(100, "Macy's")

    auto.add_revenue(1000, "Sold my bike")
    auto.add_expense(15, "Tyre Change")

    # Transfer Between Categories
    food.transfer_money(50, grocery)

    grocery.add_expense(30.72, "Chili's")
    grocery.add_expense(10.15, "Walmart")

    categories = [income,food, clothing, grocery]
    
    return categories

def print_fill_data():
    categories = get_fill_data()

    for category in categories:
        # Test Transaction Printout For Categories
        print(category, end="\n\n")

if __name__ == "__main__":
    print_fill_data()