from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DatabaseError
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

db = SQLAlchemy(app)

def make_response_no_cache(status_code):
    response = make_response('', status_code)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/healthz', methods=['GET'])
def health_check():
    if len(request.args) > 0 or request.form or request.data:
        return make_response_no_cache(400)  
    
    try:
        result = db.session.execute(text("SELECT 1")).fetchone()
        return make_response_no_cache(200 if result else 503)  
    except (OperationalError, DatabaseError):
        return make_response_no_cache(503)

@app.before_request
def limit_http_methods():
    if request.path == '/healthz' and request.method != 'GET':
        return make_response_no_cache(405)

@app.errorhandler(404)
def page_not_found(e):
    return make_response_no_cache(404)

if __name__ == '__main__':
    app.run(debug=True)
