import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

class config:
    SQLALCHEMY_DATABASE_URI = (
    f"mariadb+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False