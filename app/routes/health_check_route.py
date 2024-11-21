from flask import Blueprint
from app.controllers.health_check_controller import health_check

health_bp = Blueprint("health_check", __name__)

health_bp.route('/healthz', methods=['GET'])(health_check)

health_bp.route('/cicd', methods=['GET'])(health_check)
