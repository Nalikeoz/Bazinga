import sqlite3
import hashlib

DEFAULT_DATABASE_NAME = 'database.db'


class DataBase(object):
    def __init__(self, database_name=DEFAULT_DATABASE_NAME):
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()  # used to make interaction with the database.
        self._create_db()
        
    def _create_db(self):
        try:
            self.cursor.execute('''CREATE TABLE "users" (
            "username"	TEXT,
            "password"	TEXT
            );''')
            self.connection.commit()
            print '[+] Created DATABASE'
        except sqlite3.OperationalError:
            pass

    def add_user(self, username, password):
        """
        @param username: the new user's username(string).
        @param password: the new user's password (will be hashed before assigned to the DB)(string).

        the function gets information about a new user and adds him to the database.
        """
        hashed_password = hashlib.sha256(password).hexdigest()
        self.cursor.execute('INSERT INTO users VALUES(?,?)', (username, hashed_password))
        self.connection.commit()
        print '[+] New User has been added'

    def does_username_exists(self, username):
        """
        @param username: the user's username.
        @return: True if there's a user with the following username, otherwise returns False.
        """
        user_info = (username, )
        self.cursor.execute('SELECT * FROM users WHERE username=?', user_info)
        response = self.cursor.fetchone()
        return response is not None

    def does_user_exists(self, username, password):
        """
        @param username: the user's username.
        @param password: the user's password.
        @return: True if there's a user with the following info, otherwise returns False.
        """
        user_info = (username, hashlib.sha256(password).hexdigest())
        self.cursor.execute('SELECT * FROM users WHERE username=? and password=?', user_info)
        response = self.cursor.fetchone()
        return response is not None

    def get_user_info(self, username):
        username = (username, )
        self.cursor.execute('SELECT * FROM users WHERE username=?', username)
        user_info = self.cursor.fetchone()
        return user_info

    def close(self):
        """
        the function stops the connection between the user and the databse.
        """
        self.connection.commit()
