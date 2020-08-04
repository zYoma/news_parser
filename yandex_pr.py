import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")


def write_date(current_date):
    with open('current_date', 'w') as f:
        f.write(str(current_date))


def read_date():
    with open('current_date', 'r') as f:
        return f.read()


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    id = homework.get('id')
    status = homework.get('status')
    data = str(id) + '__' + str(status)
    last_data = read_date()
    if data == last_data:
        return f'Изминений нет.'
    else:
        write_date(data)
        if status == 'rejected':
            verdict = 'ЕСТЬ ОШИБКИ!'
        else:
            verdict = 'ПРИНЯТО!'
        return f'{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(url=url, params=params, headers=headers)
    return homework_statuses.json()


def check_status():
    new_homework = get_homework_statuses(0)
    if new_homework.get('homeworks'):
        status = parse_homework_status(new_homework.get('homeworks')[0])
        return status
    else:
        return 'Работу еще не проверили'
