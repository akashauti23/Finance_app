import unittest
from unittest import mock
import finance_app  # Assuming the finance app is named finance_app.py

class TestFinanceApp(unittest.TestCase):

    # Mock the bcrypt.hashpw function to return a predictable hash
    @mock.patch('finance_app.bcrypt.hashpw')
    def test_register_user(self, mock_bcrypt_hashpw):
        # Mock bcrypt hash output
        mock_bcrypt_hashpw.return_value = b'$2b$12$mockedhashvalue'

        # Simulate user registration
        username = 'Akash'
        password = '12345'
        
        # Mock database connection and cursor
        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor

            # Call the register_user function
            finance_app.register_user(username, password)

            # Check if the execute function was called with the expected arguments
            mock_cursor.execute.assert_called_with(
                'INSERT INTO users (username, password) VALUES (%s, %s)', 
                (username, b'$2b$12$mockedhashvalue')
            )

    # Mock the bcrypt.checkpw function to return True for valid password comparison
    @mock.patch('finance_app.bcrypt.checkpw')
    def test_login_user(self, mock_bcrypt_checkpw):
        # Mock the bcrypt checkpw to always return True
        mock_bcrypt_checkpw.return_value = True

        # Simulate user login
        username = 'Akash'
        password = '12345'

        # Mock the database fetch to return a pre-defined hashed password
        with mock.patch('finance_app.create_connection') as mock_connection:
            mock_cursor = mock.MagicMock()
            mock_connection.return_value.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (username, b'$2b$12$mockedhashvalue')

            # Call the login_user function
            result = finance_app.login_user(username, password)

            # Check that login_user returns the correct username on successful login
            self.assertEqual(result, username)
            mock_bcrypt_checkpw.assert_called_with(password.encode('utf-8'), b'$2b$12$mockedhashvalue')

if __name__ == '__main__':
    unittest.main()
