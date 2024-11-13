import mysql.connector
import bcrypt
from datetime import datetime

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "your_new_password",
    "database": "finance_db"
}

# Function to create a connection to the database
def create_connection():
    return mysql.connector.connect(**db_config)

# Function to hash the password
def hash_password(password):
    """Hashes the password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to register a user
def register_user(username, password):
    """Registers a new user by inserting their details into the database"""
    conn = create_connection()
    cursor = conn.cursor()

    if not username or not password:
        print("Username and password are required to register.")
        return

    # Hash the password before storing it
    hashed_password = hash_password(password)

    # Insert user into the users table
    try:
        cursor.execute(
            "INSERT INTO Users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        print(f"User {username} registered successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to login a user
def login_user(username, password):
    """Logs in a user by checking their credentials"""
    conn = create_connection()
    cursor = conn.cursor()

    if not username or not password:
        print("Both username and password are required for login.")
        return None

    # Query to fetch user details
    cursor.execute("SELECT ID, password FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        print("Login successful.")
        return user[0]  # Return the user ID instead of username
    else:
        print("Invalid credentials.")
        return None

# Function to add a transaction (income/expense) and check if the budget is exceeded
def add_transaction(user_id, category, amount, transaction_type):
    """Adds a transaction (income or expense) and checks for budget exceedance"""
    conn = create_connection()
    cursor = conn.cursor()

    if not category or not amount or not transaction_type:
        print("Category, amount, and transaction type are required for adding a transaction.")
        return

    try:
        date = input("Enter date (YYYY-MM-DD): ") or datetime.now().strftime("%Y-%m-%d")
        description = input("Enter description: ") or "No description provided"

        # Insert the transaction into the Transactions table
        cursor.execute("""
            INSERT INTO Transactions (user_id, category, amount, date, description, transaction_type) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, category, amount, date, description, transaction_type))
        conn.commit()

        # Check if the transaction is an expense and if it exceeds the budget
        if transaction_type == 'expense':
            cursor.execute("""
                SELECT amount FROM Budgets WHERE user_id = %s AND category = %s
            """, (user_id, category))
            budget = cursor.fetchone()

            if budget:
                budget_amount = budget[0]

                # Calculate the total expenses for the current month
                cursor.execute("""
                    SELECT SUM(amount) FROM Transactions 
                    WHERE user_id = %s AND transaction_type = 'expense' AND category = %s AND date LIKE %s
                """, (user_id, category, f"{datetime.now().strftime('%Y-%m')}%"))
                total_expenses_month = cursor.fetchone()[0] or 0

                # Compare total expenses against the budget
                if total_expenses_month > budget_amount:
                    print(f"Alert: You have exceeded your total budget for {category}. Total expenses: {total_expenses_month}, Budget: {budget_amount}.")
                else:
                    print(f"Your {category} budget is under control. You have spent {total_expenses_month} out of {budget_amount} this month.")
            else:
                print(f"No budget set for {category}.")
        
        print(f"{transaction_type.capitalize()} of {amount} added successfully.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# Function to generate monthly and yearly reports
def generate_reports(user_id):
    """Generates and displays monthly and yearly financial reports"""
    conn = create_connection()
    cursor = conn.cursor()

    month = input("Enter month (YYYY-MM): ")
    if not month:
        print("Month is required for generating a report.")
        return

    cursor.execute(
        "SELECT SUM(amount) FROM Transactions WHERE user_id = %s AND date LIKE %s",
        (user_id, f"{month}%")
    )
    total_income_expenses = cursor.fetchone()
    print(f"Total transactions in {month}: {total_income_expenses[0]}")

    year = input("Enter year (YYYY): ")
    if not year:
        print("Year is required for generating a report.")
        return

    cursor.execute(
        "SELECT SUM(amount) FROM Transactions WHERE user_id = %s AND date LIKE %s",
        (user_id, f"{year}%")
    )
    total_income_expenses_year = cursor.fetchone()
    print(f"Total transactions in {year}: {total_income_expenses_year[0]}")

    cursor.execute("SELECT * FROM Transactions WHERE user_id = %s", (user_id,))
    report = cursor.fetchall()  # This fetches all the data
    cursor.close()
    conn.close()
    return report

# Function to set a budget for a user
def set_budget(user_id, category, amount):
    """Set or update a budget for a category"""
    conn = create_connection()
    cursor = conn.cursor()

    if not category or not amount:
        print("Category and amount are required for setting a budget.")
        return

    # Check if the budget already exists for the specified category
    cursor.execute("""
        SELECT * FROM Budgets WHERE user_id = %s AND category = %s
    """, (user_id, category))
    existing_budget = cursor.fetchone()

    if existing_budget:
        # If budget exists, update it
        cursor.execute("""
            UPDATE Budgets SET amount = %s WHERE user_id = %s AND category = %s
        """, (amount, user_id, category))
        print(f"Budget for {category} updated to {amount}.")
    else:
        # If no budget exists, insert a new one
        cursor.execute("""
            INSERT INTO Budgets (user_id, category, amount) VALUES (%s, %s, %s)
        """, (user_id, category, amount))
        print(f"Budget for {category} set to {amount}.")
    
    conn.commit()
    cursor.close()
    conn.close()

# Delete the user login details
def delete_account(user_id):
    """Delete the user account"""
    conn = create_connection()
    cursor = conn.cursor()

    if not user_id:
        print("User ID is required to delete the account.")
        return

    conf = input("Are you sure you want to delete? (Y/N): ").lower()
    if conf == "y":
        try:
            cursor.execute("DELETE FROM Users WHERE ID = %s", (user_id,))
            conn.commit()
            print("Account deleted successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Cancelled the delete process.")

# Main menu function to navigate the application
def main():
    print("Welcome to the Personal Finance Manager")

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            # Register a new user
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            register_user(username, password)
        elif choice == '2':
            # Login an existing user
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            user_id = login_user(username, password)
            if user_id:
                print(f"Welcome, {user_id}")
                while True:
                    print("\n1. Add Income")
                    print("2. Add Expense")
                    print("3. Set Budget")
                    print("4. Generate Reports")
                    print("5. Delete Account")
                    print("6. Logout")
                    action_choice = input("Select an option: ")

                    if action_choice == '1':
                        category = input("Enter income category: ")
                        amount = input("Enter amount: ")
                        if amount:
                            add_transaction(user_id, category, float(amount), 'income')
                        else:
                            print("Amount is required for income.")
                    elif action_choice == '2':
                        category = input("Enter expense category: ")
                        amount = input("Enter amount: ")
                        if amount:
                            add_transaction(user_id, category, float(amount), 'expense')
                        else:
                            print("Amount is required for expense.")
                    elif action_choice == '3':
                        category = input("Enter category to set budget for: ")
                        amount = input("Enter budget amount: ")
                        if amount:
                            set_budget(user_id, category, float(amount))
                        else:
                            print("Amount is required to set a budget.")
                    elif action_choice == '4':
                        generate_reports(user_id)
                    elif action_choice == '5':
                        delete_account(user_id)
                    elif action_choice == '6':
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Login failed.")
        elif choice == '3':
            print


if __name__ == '__main__':
    main()
