import mysql.connector
import bcrypt
from getpass import getpass
import datetime

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "your_new_password",
    "database": "finance_app"
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

    # Hash the password before storing it
    hashed_password = hash_password(password)

    # Insert user into the users table
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
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

    # Query to fetch user details
    cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
        print("Login successful.")
        return user[0]  # Return the username (or user ID if needed)
    else:
        print("Invalid credentials.")
        return None

# Function to add a transaction (income/expense)
def add_transaction(user_id, category, amount, transaction_type):
    """Adds a transaction (income or expense)"""
    conn = create_connection()
    cursor = conn.cursor()

    date = input("Enter date (YYYY-MM-DD): ") or datetime.now().strftime("%Y-%m-%d")
    description = input("Enter description: ")

    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, category, amount, date, description, transaction_type) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, category, amount, date, description, transaction_type)
        )
        conn.commit()
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

    # Monthly report
    month = input("Enter month (YYYY-MM): ")
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = %s AND date LIKE %s",
        (user_id, f"{month}%")
    )
    total_income_expenses = cursor.fetchone()
    print(f"Total transactions in {month}: {total_income_expenses[0]}")

    # Yearly report
    year = input("Enter year (YYYY): ")
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = %s AND date LIKE %s",
        (user_id, f"{year}%")
    )
    total_income_expenses_year = cursor.fetchone()
    print(f"Total transactions in {year}: {total_income_expenses_year[0]}")

    cursor.close()
    conn.close()

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
                    print("3. Generate Reports")
                    print("4. Logout")
                    action_choice = input("Select an option: ")

                    if action_choice == '1':
                        category = input("Enter income category: ")
                        amount = float(input("Enter amount: "))
                        add_transaction(user_id, category, amount, 'income')
                    elif action_choice == '2':
                        category = input("Enter expense category: ")
                        amount = float(input("Enter amount: "))
                        add_transaction(user_id, category, amount, 'expense')
                    elif action_choice == '3':
                        generate_reports(user_id)
                    elif action_choice == '4':
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Login failed.")
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()