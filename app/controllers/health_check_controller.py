from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DatabaseError
from app.utilities.response_utils import response_handler
from app.services.health_check_service import get_health

def health_check():
    if len(request.args) > 0 or request.form or request.data:
        return response_handler(400) 
    
    if request.path == '/healthz' and request.method == 'GET':
        res = get_health()
        if res:
            return response_handler(200)
        else: 
            return response_handler(503)
        
