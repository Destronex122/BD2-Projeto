from django.db import connection

def admin_status(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT IsAdmin(%s)", [request.user.id])
        result = cursor.fetchone()
        is_admin = result[0]
    return {'is_admin': 1, 'role' : "admin"}

def GetFields(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GetFields(%s)", [request.user.id])
        result = cursor.fetchall()
        
    # Transformar a lista de tuplas em uma lista de dicionários
    campos = [
        {'campoid': row[0], 'nome': row[2]} 
        for row in result
    ]
    return {'quintas': campos}