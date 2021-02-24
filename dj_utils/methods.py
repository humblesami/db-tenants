import sys
import json
import pytz
import base64
#import requests
import threading
import traceback

from dateutil import parser
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.apps import apps
from django.db import connection
from django.core.files.base import ContentFile

from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string


def dt_now():
    dt = datetime.now()
    dt = dt.replace(tzinfo=pytz.utc)
    return dt


def dt_span_seconds(dt1, dt2=None):
    if not dt2:
        dt2 = dt_now()
    diff = dt2 - dt1
    return diff.seconds


def add_interval(interval_type, inc, dt=None):
    inc = int(inc)
    if not dt:
        dt = datetime.now()
    if interval_type == 'years':
        dt = dt + relativedelta(years=inc)
    if interval_type == 'months':
        dt = dt + relativedelta(months=inc)
    if interval_type == 'days':
        dt = dt + relativedelta(days=inc)
    if interval_type == 'hours':
        dt = dt + relativedelta(hours=inc)
    if interval_type == 'minutes':
        dt = dt + relativedelta(minutes=inc)
    if interval_type == 'seconds':
        dt = dt + relativedelta(seconds=inc)
    return dt


def now_str(format=''):
    dt = datetime.now()
    time_now_str = change_datetime_format(dt, format)
    return time_now_str


def get_user_name(user):
    name = False
    if user.first_name:
        name = user.first_name
        if user.last_name:
            name += ' ' + user.last_name
    elif user.last_name:
        name += user.last_name
    else:
        name = user.username
    return name


def log_error(ex):
    return ''


def change_datetime_format(dt, format=''):
    if type(dt) is str:
        dt = parser.parse(dt)
    if not format:
        format = "%Y-%m-%dT%H:%M:%SZ"
    dt_str = dt.strftime(format)
    return dt_str


def execute_update(query):
    cr = connection.cursor()
    res = cr.execute(query)
    return res


def stringify_fields(dict_object):
    if dict_object.get('updated_at'):
        dict_object['updated_at'] = str(dict_object['updated_at'])
    if dict_object.get('created_at'):
        dict_object['created_at'] = str(dict_object['created_at'])
    if dict_object.get('updated_by'):
        dict_object['updated_by'] = str(dict_object['updated_by'])
    if dict_object.get('created_by'):
        dict_object['created_by'] = str(dict_object['created_by'])


def execute_read(query):
    cr = connection.cursor()
    cr.execute(query)
    res = cr.dictfetchall()
    return res


def set_obj_attrs(dict_key_values, py_obj):
    for prop in dict_key_values:
        py_obj. __setattr__(prop, dict_key_values[prop])


def base64_str_to_file(data, file_name):
    if 'data:' in data and ';base64,' in data:
        header, data = data.split(';base64,')
    try:
        decoded_file = base64.b64decode(data)
    except:
        raise ValueError('Invalid binary')

    return ContentFile(decoded_file, name=file_name)


def choices_to_list(choice_list):
    lst = []
    for choice in choice_list:
        lst.append({'id': choice[0], 'name': str(choice[1])})
    return lst


# def http(req_url, headers=None):
#     try:
#         res = ''
#         if headers:
#             res = requests.get(req_url, headers=headers)
#         else:
#             res = requests.get(req_url)
#         res = res.content
#     except:
#         res = 'Request failed because ' + str(sys.exc_info())
#         print(res)
#     return res
#
#
# def http_request(req_url):
#     try:
#         res = requests.get(req_url)
#         res = res._content.decode("utf-8")
#         return res
#     except:
#         res = get_error_message()
#         return res

def get_model(app_name, model_name):
    try:
        model = apps.get_model(app_name, model_name)
        return model
    except:
        return 'model not found'


def replace_key_in_dict(values, old_key, new_key):
    for obj in values:
        obj[new_key] = obj.pop(old_key)

    return values


def threaded_operation(operation, args):
    obj = threading.Thread(target=operation, args=args)
    obj.start()


def send_mail_in_thread(mail_data, html_message):
    send_mail(mail_data['subject'], '', "noreply@django.com", mail_data['recipients'], html_message=html_message)


def send_email(mail_data):
    html_message = mail_data['message']
    if mail_data.get('template_name'):
        html_message = render_to_string(mail_data['template_name'], mail_data)
    threaded_operation(send_mail_in_thread , args=(mail_data, html_message))


def send_email_on_creation(email_data):
    subject = email_data['subject']
    post_info = email_data['post_info']
    audience = email_data['audience']
    template_data = email_data['template_data']
    template_name = email_data['template_name']
    token_required = email_data.get('token_required')
    mail_data = {
        'subject': subject,
        'audience': audience,
        'template_data': template_data,
        'template_name': template_name,
        'token_required': token_required,
        'post_info': post_info
    }
    send_email(mail_data)


def get_error_message():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\site-packages' in er:
            error_message += " " + er
    return error_message


def bytes_to_json(my_bytes_value):
    my_json = {'error': 'Invalid bytes value to get json'}
    try:
        my_json = my_bytes_value.decode('utf8').replace("'", '"')
        my_json = json.loads(my_json)
    except:
        pass
    return my_json


def produce_res_json(data):
    res = {'status': 'success', 'data': data }
    data = JsonResponse(res)
    return data


def produce_error_json(error_message='', data=None):
    if not error_message:
        error_message = get_error_message()
    res = {'status': 'error', 'message': error_message}
    if data:
        res['data'] = data
    data = JsonResponse(res)
    return data


def produce_custom_error_json(error_data):
    if isinstance(error_data, dict):
        error_data['status'] = 'error'
    else:
        error_data = {'status': 'error', 'message': 'Invalid error data'}
    data = JsonResponse(error_data)
    return data

