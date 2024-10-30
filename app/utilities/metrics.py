from statsd import StatsClient

# Configure StatsD client
statsd_client = StatsClient(host='localhost', port=8125)

def record_api_call(api_name):
    statsd_client.incr(f'api.calls.{api_name}')

def record_api_duration(api_name, duration):
    statsd_client.timing(f'api.duration.{api_name}', duration)

def record_database_query_duration(duration):
    statsd_client.timing('database.query.duration', duration)

def record_s3_call_duration(duration):
    statsd_client.timing('s3.call.duration', duration)
