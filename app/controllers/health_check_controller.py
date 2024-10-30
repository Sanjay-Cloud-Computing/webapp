import logging
from flask import request
from time import time
from app.utilities.response_utils import response_handler
from app.services.health_check_service import get_health
from app.utilities.metrics import statsd_client, record_api_call, record_api_duration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def health_check():
    start_time = time()
    record_api_call('health_check')  # Track API call
    
    try:
        if len(request.args) > 0 or request.form or request.data:
            statsd_client.incr('health_check.error')  # Log error count for invalid requests
            record_api_duration('health_check', (time() - start_time) * 1000)  # Log API duration
            logger.warning("ERROR: Invalid request format", extra={"severity": "ERROR"})
            return response_handler(400)
        
        if request.path == '/healthz' and request.method == 'GET':
            res = get_health()
            if res:
                logger.info("Health check successful", extra={"severity": "INFO"})
                record_api_duration('health_check', (time() - start_time) * 1000)
                return response_handler(200)
            else:
                statsd_client.incr('health_check.error')  # Track health check failure
                logger.error("FATAL: Health check failed", extra={"severity": "FATAL"})
                record_api_duration('health_check', (time() - start_time) * 1000)
                return response_handler(503)
                
    except Exception as e:
        statsd_client.incr('health_check.error')
        logger.exception("FATAL: Exception during health check", extra={"severity": "FATAL"})
        record_api_duration('health_check', (time() - start_time) * 1000)
        return response_handler(500)

        
