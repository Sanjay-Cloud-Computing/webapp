from flask import request, jsonify, abort, make_response
from .. import db
from flask_httpauth import HTTPBasicAuth
from app.models.user_model import User
from app.services.login_user_service import AuthService
from app.utilities.response_utils import response_handler
from app.utilities.utc_convert_datetime import format_datetime
from app.services.health_check_service import get_health
from app.utilities.check_table_utils import check_and_create_users_table
from app.utilities.utc_convert_datetime import change_date_str

auth = HTTPBasicAuth()

auth_service = AuthService()

@auth.verify_password
def verify_password(username, password):
    
    if len(request.args) > 0:
        return abort(response_handler(400))
    if get_health():
        check_and_create_users_table()
        user = auth_service.verify_user_creds(username, password)
        if user:
            return user
        else:
            abort(response_handler(401))
    else:
        abort(response_handler(503))


def get_user_details():

    user_data = db.session.query(User).filter_by(email=auth.username()).first()
    response_body = {
                "id": user_data.id,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "email": user_data.email, 
                "account_created": change_date_str(user_data.account_created),
                "account_updated": change_date_str(user_data.account_updated)
                }
    response = make_response(jsonify(response_body), 200) 
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Content-Type'] = 'application/json'
    return response
    
def update_user_details():
    
    if not request.data or request.data is None or len(request.args) > 0 or request.data.strip() == b'{}':
        return response_handler(400)
    if not request.content_type or request.content_type != 'application/json':
        return response_handler(400)
    if not request.data or request.data.strip() == b'':
        return response_handler(400)
    
    data = request.get_json()
    user_data = db.session.query(User).filter_by(email=auth.username()).first()
    allowed_fields = {"first_name", "last_name", "password"}

    if not set(data.keys()).issubset(allowed_fields):
        return response_handler(400)

    try:
        auth_service.update_user(user_data.id,data)
        return response_handler(204)
    
    except ValueError as ve:
        return response_handler(400)
    
    except Exception as e:
        return response_handler(400)