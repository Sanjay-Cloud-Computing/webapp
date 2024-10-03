from flask import make_response

def response_handler(status_code):
    response = make_response('', status_code)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Content-Length'] = '0'
    response.headers['Content-Type'] = 'application/json'
    return response