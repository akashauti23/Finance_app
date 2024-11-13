import unittest
from unittest import mock
import finance_app  # Assuming the finance app is named finance_app.py

class TestFinanceApp(unittest.TestCase):

    @mock.patch('finance_app.bcrypt.hashpw')
    def test_register_user(self, mock_bcrypt_hashpw):
        mock_bcrypt_hashpw.return_value = b'$2b$12$mockedhashvalue'
        username = 'Akash'
        password = '12345'
        
        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor

            finance_app.register_user(username, password)
            # Ensure the table name matches the actual implementation
            mock_cursor.execute.assert_called_with(
                'INSERT INTO Users (username, password) VALUES (%s, %s)',  # Correct capitalization of Users
                (username, b'$2b$12$mockedhashvalue')
            )

    def test_add_transaction(self):
        user_id = 1
        category = 'Food'
        amount = 100.0
        transaction_type = 'expense'
        
        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor

            with mock.patch('finance_app.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = '2024-11-13'

                finance_app.add_transaction(user_id, category, amount, transaction_type)
                mock_cursor.execute.assert_called_with(
                    "INSERT INTO Transactions (user_id, category, amount, date, description, transaction_type) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, category, amount, '2024-11-13', '', transaction_type)
                )

    def test_delete_account(self):
        user_id = 1

        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor

            with mock.patch('builtins.input', return_value='Y'):
                finance_app.delete_account(user_id)
                mock_cursor.execute.assert_called_with(
                    "DELETE FROM Users WHERE ID = %s", (user_id,)
                )

    def test_generate_report(self):
        user_id = 1

        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor
            
            # Mock the result of fetchall to return the expected data
            mock_cursor.fetchall.return_value = [
                (1, 'Food', 50, '2024-11-10', 'Lunch', 'expense'),
                (1, 'Salary', 500, '2024-11-01', 'Monthly salary', 'income')
            ]

            # Call the function to generate report
            report = finance_app.generate_reports(user_id)
            expected_report = [
                (1, 'Food', 50, '2024-11-10', 'Lunch', 'expense'),
                (1, 'Salary', 500, '2024-11-01', 'Monthly salary', 'income')
            ]

            # Verify if the generated report matches the expected report
            self.assertEqual(report, expected_report)

            # Check that the execute method was called with the correct SQL query
            mock_cursor.execute.assert_called_with(
                "SELECT * FROM Transactions WHERE user_id = %s", (user_id,)
            )

if __name__ == '__main__':
    unittest.main()
