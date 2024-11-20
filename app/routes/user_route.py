from flask import Blueprint,request
from app.controllers.user_controller import create_user
from app.controllers.verification_controller import verify_email

user_bp = Blueprint('user',__name__)
verify_bp = Blueprint('verify',__name__)

user_bp.route('/user', methods=['POST'])(create_user)
verify_bp.route('/verify', methods=['GET'])(verify_email)
