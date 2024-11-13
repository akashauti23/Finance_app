# Personal Finance Manager

## Description
The **Personal Finance Manager** is a command-line application built using Python that allows users to manage their personal finances. The application supports features such as:

- **User Registration and Login:** Create and manage accounts with secure passwords.
- **Track Income and Expenses:** Add income and expense records, including categories like salary, rent, groceries, etc.
- **Generate Financial Reports:** View reports summarizing income, expenses, and savings for a specified period.

This application helps individuals keep track of their financial health by providing a simple, easy-to-use interface for managing personal transactions.

---

## Features

- **User Registration**: Allows users to create an account with a username and password.
- **User Login**: Allows users to log in securely.
- **Income/Expense Management**: Add income or expense entries, and categorize them.
- **Financial Report Generation**: Generate a report showing total income, expenses, and savings over a given time range.
- **Delete Account**: Allow users to delete the account securely.
- **Data Persistence**: All user data is stored in a MySQL database for persistence.

---

## Requirements

- **Python 3.11.6**
- **MySQL Database**

---

## Installation Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/akashauti23/Finance_app.git

2. **Start the Application**
   ```bash
   python finance_app.py

3. **To Run the Mock Test**
   ```bash
   python -m unittest tests/test_finance_app.py
