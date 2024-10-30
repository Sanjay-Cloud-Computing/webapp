from flask import Blueprint
from app.controllers.image_controller import upload_profile_picture, get_profile_picture, delete_profile_picture

profile_picture_bp = Blueprint("profile_picture", __name__)

profile_picture_bp.route('/v1/user/self/pic', methods=['POST'])(upload_profile_picture)
profile_picture_bp.route('/v1/user/self/pic', methods=['GET'])(get_profile_picture)
profile_picture_bp.route('/v1/user/self/pic', methods=['DELETE'])(delete_profile_picture)
