from django.db import connection

def admin_status(request):
    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT IsAdmin(%s)", [request.user.id])
    #     result = cursor.fetchone()
    #     is_admin = result[0]
    # return {'is_admin': is_admin}
    return {'is_admin': 1}
