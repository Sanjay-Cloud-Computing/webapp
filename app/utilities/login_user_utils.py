import bcrypt
import re

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def hash_password(password, salt_rounds=12):
    salt = bcrypt.gensalt(rounds=salt_rounds)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(stored_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8'))


def format_user_repr(username):
    return f"<User {username}>"

def is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None
