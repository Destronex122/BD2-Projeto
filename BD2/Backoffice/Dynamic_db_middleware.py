from django.db import connection
from django.http import HttpResponseForbidden
from threading import local


_user_context = local()

def set_db_role(role, password):
    """Define a role e a senha no contexto local."""
    _user_context.role = role
    _user_context.password = password

def get_db_role():
    """Obtém a role e senha do contexto local."""
    return getattr(_user_context, 'role', None), getattr(_user_context, 'password', None)

class DynamicDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        role, password = get_db_role()

        if role and password:
            connection.settings_dict['USER'] = role
            connection.settings_dict['PASSWORD'] = password
        else:
          
            connection.settings_dict['USER'] = 'aluno6'
            connection.settings_dict['PASSWORD'] = 'di!912877'

        response = self.get_response(request)
        return response
