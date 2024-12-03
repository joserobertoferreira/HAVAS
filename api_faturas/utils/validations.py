import re


class Validations:
    @staticmethod
    def validate_email(email):
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            raise ValueError('Invalid email format')

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')

    @staticmethod
    def validate_username(username):
        if len(username) < 6:
            raise ValueError('Username must be at least 6 characters long')

    @staticmethod
    def validate_name(name):
        if len(name) < 3:
            raise ValueError('Name must be at least 3 characters long')

    @staticmethod
    def validate_age(age):
        if age < 18:
            raise ValueError('Age must be at least 18 years old')
