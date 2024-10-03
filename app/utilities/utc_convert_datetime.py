from datetime import datetime,timezone

def format_datetime():
    print(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def change_date_str(date_time):
    return datetime.strftime(date_time,"%Y-%m-%dT%H:%M:%S.000Z")

