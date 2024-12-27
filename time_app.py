import json
from datetime import datetime, timedelta
import pytz
from wsgiref.simple_server import make_server


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    if method == 'GET' and path == '/':
        return handle_root(environ, start_response)
    elif method == 'GET' and path.startswith('/'):
        return handle_timezone(environ, start_response, path[1:])
    elif method == 'POST' and path == '/api/v1/time':
        return handle_api_time(environ, start_response)
    elif method == 'POST' and path == '/api/v1/date':
        return handle_api_date(environ, start_response)
    elif method == 'POST' and path == '/api/v1/datediff':
        return handle_api_datediff(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b"Not Found"]


def get_server_timezone():
    return pytz.timezone('UTC')


def handle_root(environ, start_response):
    tz = get_server_timezone()
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [f"<html><body><h1>Current server time: {current_time}</h1></body></html>".encode('utf-8')]


def handle_timezone(environ, start_response, tz_name):
    try:
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [f"<html><body><h1>Current time in {tz_name}: {current_time}</h1></body></html>".encode('utf-8')]
    except pytz.UnknownTimeZoneError:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return [b"Unknown timezone"]


def handle_api_time(environ, start_response):
    try:
        request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))).decode('utf-8')
        data = json.loads(request_body) if request_body else {}
        tz_name = data.get('tz', 'UTC')
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
        response = {'time': current_time}
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(response).encode('utf-8')]
    except pytz.UnknownTimeZoneError:
        start_response('400 Bad Request', [('Content-Type', 'application/json')])
        return [json.dumps({'error': 'Unknown timezone'}).encode('utf-8')]


def handle_api_date(environ, start_response):
    try:
        request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))).decode('utf-8')
        data = json.loads(request_body) if request_body else {}
        tz_name = data.get('tz', 'UTC')
        tz = pytz.timezone(tz_name)
        current_date = datetime.now(tz).strftime('%Y-%m-%d')
        response = {'date': current_date}
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(response).encode('utf-8')]
    except pytz.UnknownTimeZoneError:
        start_response('400 Bad Request', [('Content-Type', 'application/json')])
        return [json.dumps({'error': 'Unknown timezone'}).encode('utf-8')]


def handle_api_datediff(environ, start_response):
    try:
        request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))).decode('utf-8')
        data = json.loads(request_body)
        start_date = parse_date(data.get('start'))
        end_date = parse_date(data.get('end'))
        diff = end_date - start_date
        response = {'difference': str(diff)}
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps(response).encode('utf-8')]
    except (ValueError, KeyError) as e:
        start_response('400 Bad Request', [('Content-Type', 'application/json')])
        return [json.dumps({'error': str(e)}).encode('utf-8')]


def parse_date(date_info):
    if not date_info or 'date' not in date_info:
        raise ValueError('Invalid date input')
    date_str = date_info['date']
    tz_name = date_info.get('tz', 'UTC')
    tz = pytz.timezone(tz_name)
    naive_date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S') if ' ' in date_str else datetime.strptime(date_str,
                                                                                                            '%I:%M%p %Y-%m-%d')
    return tz.localize(naive_date)


if __name__ == '__main__':
    with make_server('', 8000, application) as server:
        print("Serving on port 8000...")
        server.serve_forever()
