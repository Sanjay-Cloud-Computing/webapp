from flask import Blueprint
from app.controllers.login_user_controller import auth,get_user_details, update_user_details

auth_bp = Blueprint("login_user", __name__)

auth_bp.route('/v2/user/self', methods=['GET'])(auth.login_required(get_user_details))
auth_bp.route('/v2/user/self', methods=['PUT'])(auth.login_required(update_user_details))


