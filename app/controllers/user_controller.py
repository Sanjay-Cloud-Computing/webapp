from flask import request,abort, make_response,jsonify
from datetime import datetime
from app.services.user_service import userService
from app.utilities.response_utils import response_handler
from app.services.health_check_service import get_health
from app.utilities.utc_convert_datetime import format_datetime,change_date_str

user_service = userService()

def create_user():
    
    try:
        data = request.get_json()
        if data is None or len(request.args) > 0:
            return response_handler(400)
        healthCheck = get_health()
        if healthCheck:
            newUser = user_service.create_user(data)
            response_body = {
                "id": newUser.id,
                "first_name": newUser.first_name,
                "last_name": newUser.last_name,
                "email": newUser.email, 
                "account_created": change_date_str(newUser.account_created),
                "account_updated": change_date_str(newUser.account_updated)
                }
            response = make_response(jsonify(response_body), 201) 
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return abort(response_handler(503))
        
    except ValueError:
        return response_handler(400)
    