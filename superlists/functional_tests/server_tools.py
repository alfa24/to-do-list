from fabric.api import run
from fabric.context_managers import settings


def _get_manage_dot_py(host):
    """получить manage.py"""

    return f'~/sites/{host}/source/virtualenv/bin/python ~/sites/{host}/source/superlists/manage.py'


def reset_database(host):
    """обнулить базу данных"""

    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'aleks@{host}'):
        run(f'{manage_dot_py} flush --noinput')


def create_session_on_server(host, email):
    """создать сессию на сервере"""

    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'aleks@{host}'):
        session_key = run(f'{manage_dot_py} create_session {email}')
        return session_key.strip()

