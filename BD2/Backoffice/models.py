from pymongo import MongoClient
from pymongo import MongoClient 
from bson.json_util import dumps
import json
from django.http import JsonResponse
from django.db import connection
from django.db import models


dbname='Interaction_Database'
dbcollection="coordinates"

client = MongoClient('mongodb+srv://admin:admin@bdii22470.9hleq.mongodb.net/?retryWrites=true&w=majority&appName=BDII22470/')
db = client[dbname]

# def save_marker(request):
#     markers_collection = db[dbcollection]
#     markers_collection.insert_one(request)
#     return



# def save_polygon(request):
#     markers_collection = db[dbcollection]
#     markers_collection.insert_one(request)
#     return~

def save_polygon(request):
    # Verifica se a solicitação é do tipo POST
    if request.method == 'POST':
        # Extrai os dados do corpo da solicitação
        data = json.loads(request.body)
        
        # Aqui você pode querer validar os dados antes de salvar
        coordinates = data.get('coordinates')
        title = data.get('title')
        description = data.get('description')

        if coordinates and title:  # Verifica se as informações necessárias estão presentes
            markers_collection = db[dbcollection]
            # Cria um dicionário para o novo documento
            new_polygon = {
                "coordinates": coordinates,
                "title": title,
                "description": description
            }
            markers_collection.insert_one(new_polygon)
            return JsonResponse({'status': 'success', 'message': 'Polygon saved successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed.'}, status=405)



# def load_markers(request):
#     """
#     Load markers from the database and return them as a list of JSON objects.
    
#     Returns:
#         str: A JSON string representing the list of markers.
#     """
#     markers_collection = db[dbcollection]
#     markers = markers_collection.find({"lat": {"$exists": True}})
    
#     # Convert the cursor to a list and then to JSON in one step
#     json_data = dumps([marker for marker in markers], indent=2)
#     print(json_data)
    
#     return json_data

def load_markers(request):
    try:
        # Query para buscar os dados dos campos
        query = """
            SELECT campoid, coordenadas, nome, morada, cidade, pais, datacriacao
            FROM campos
            WHERE coordenadas IS NOT NULL;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        
        # Formatando os dados para retornar como JSON
        markers = []
        for row in rows:
            marker = {
                'campoid': row[0],
                'coordenadas': row[1],
                'nome': row[2],
                'morada': row[3],
                'cidade': row[4],
                'pais': row[5],
                'datacriacao': row[6]
            }
            markers.append(marker)
        
        # Retornando os dados no formato JSON
        return JsonResponse(markers, safe=False)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def load_vineyards(request):
    field_id = request.GET.get('vineyard')
    if not field_id:
        return JsonResponse({'error': 'Field ID is required'}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT f_getvineyards(%s)", [field_id])
            result = cursor.fetchone()  # Obtém o JSON como string

            if not result or not result[0]:
                return JsonResponse([], safe=False)  # Retorna uma lista vazia se não houver dados

            vineyards = json.loads(result[0])  # Decodifica o JSON retornado

            # Decodifica o campo "Coordenadas" de cada vinha
            for vineyard in vineyards:
                vineyard['Coordenadas'] = json.loads(vineyard['Coordenadas'])

            return JsonResponse(vineyards, safe=False)
    except Exception as e:
        print(f"Error in load_vineyards: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Campos(models.Model):
    campoid = models.AutoField(primary_key=True)
    coordenadas = models.JSONField()
    nome = models.TextField()
    morada = models.TextField()
    cidade = models.TextField()
    pais = models.TextField()
    datacriacao = models.DateField()
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'campos'


class Cargo(models.Model):
    cargoid = models.AutoField(primary_key=True)
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'cargo'


class Castas(models.Model):
    castaid = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'castas'


class Clientes(models.Model):
    clienteid = models.OneToOneField('Users', models.DO_NOTHING, db_column='clienteid', primary_key=True)
    isempresa = models.BooleanField()
    nif = models.IntegerField()
    contacto = models.TextField()
    morada = models.TextField()
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clientes'


class Colheitas(models.Model):
    colheitaid = models.AutoField(primary_key=True)
    vinhaid = models.ForeignKey('Vinhas', models.DO_NOTHING, db_column='vinhaid', blank=True, null=True)
    pesototal = models.DecimalField(max_digits=65535, decimal_places=65535)
    precoportonelada = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    datapesagem = models.DateField(blank=True, null=True)
    periodoid = models.ForeignKey('Periodos', models.DO_NOTHING, db_column='periodoid', blank=True, null=True)
    previsaofimcolheita = models.DateField(blank=True, null=True)
    terminada = models.BooleanField()
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'colheitas'


class Contratos(models.Model):
    contratoid = models.AutoField(primary_key=True)
    nome = models.TextField()
    clienteid = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='clienteid', blank=True, null=True)
    idpedido_item = models.ForeignKey('PedidosItem', models.DO_NOTHING, db_column='idpedido_item', blank=True, null=True)
    datainicio = models.DateField()
    datafim = models.DateField(blank=True, null=True)
    qtdeestimada = models.DecimalField(max_digits=65535, decimal_places=65535)
    precoestimado = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    qtdefinal = models.DecimalField(max_digits=65535, decimal_places=65535)
    precofinal = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contratos'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):

    class Meta:
        managed = False
        db_table = 'django_session'


class Estadosaprovacoes(models.Model):
    idaprovacao = models.AutoField(primary_key=True)
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'estadosaprovacoes'


class Estadosrecibo(models.Model):
    idestado = models.AutoField(primary_key=True)
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'estadosrecibo'


class Estadostransporte(models.Model):
    idestado = models.AutoField(primary_key=True)
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'estadostransporte'


class Metodospagamento(models.Model):
    idmetodopagamento = models.AutoField(primary_key=True)
    nome = models.TextField()

    class Meta:
        managed = False
        db_table = 'metodospagamento'


class NotasColheitas(models.Model):
    notaid = models.AutoField(primary_key=True)
    colheitaid = models.ForeignKey(Colheitas, models.DO_NOTHING, db_column='colheitaid', blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    data = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notas_colheitas'


class NotasPedidos(models.Model):
    notaid = models.AutoField(primary_key=True)
    pedidoid = models.ForeignKey('Pedidos', models.DO_NOTHING, db_column='pedidoid', blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    data = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notas_pedidos'


class Pedidos(models.Model):
    pedidoid = models.AutoField(primary_key=True)
    nome = models.TextField()
    clienteid = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='clienteid', blank=True, null=True)
    datainicio = models.DateField()
    datafim = models.DateField(blank=True, null=True)
    aprovadorid = models.ForeignKey('Users', models.DO_NOTHING, db_column='aprovadorid', blank=True, null=True)
    precoestimado = models.TextField(blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedidos'


class PedidosItem(models.Model):
    idpedido_item = models.AutoField(primary_key=True)
    idpedido = models.ForeignKey(Pedidos, models.DO_NOTHING, db_column='idpedido', blank=True, null=True)
    castaid = models.ForeignKey(Castas, models.DO_NOTHING, db_column='castaid', blank=True, null=True)
    quantidade = models.DecimalField(max_digits=65535, decimal_places=65535)
    estadoaprovacaoid = models.ForeignKey(Estadosaprovacoes, models.DO_NOTHING, db_column='estadoaprovacaoid', blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedidos_item'


class Periodos(models.Model):
    periodoid = models.AutoField(primary_key=True)
    datainicio = models.DateField()
    datafim = models.DateField()
    ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'periodos'


class Pesagens(models.Model):
    pesagemid = models.AutoField(primary_key=True)
    pesobruto = models.DecimalField(max_digits=10, decimal_places=2)
    pesoliquido = models.DecimalField(max_digits=10, decimal_places=2)
    datadepesagem = models.DateField()
    colheitaid = models.ForeignKey(Colheitas, models.DO_NOTHING, db_column='colheitaid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pesagens'


class Recibos(models.Model):
    reciboid = models.AutoField(primary_key=True)
    idcontrato = models.ForeignKey(Contratos, models.DO_NOTHING, db_column='idcontrato', blank=True, null=True)
    datainicio = models.DateField()
    precofinal = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    colheitaid = models.ForeignKey(Colheitas, models.DO_NOTHING, db_column='colheitaid', blank=True, null=True)
    metodopagamento = models.ForeignKey(Metodospagamento, models.DO_NOTHING, db_column='metodopagamento', blank=True, null=True)
    estadoid = models.ForeignKey(Estadosrecibo, models.DO_NOTHING, db_column='estadoid', blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recibos'


class Transportes(models.Model):
    idtransporte = models.AutoField(primary_key=True)
    reciboid = models.ForeignKey(Recibos, models.DO_NOTHING, db_column='reciboid', blank=True, null=True)
    nome = models.TextField()
    morada = models.TextField()
    data = models.DateField()
    precotransporte = models.DecimalField(max_digits=65535, decimal_places=65535)
    precokm = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    estadoid = models.ForeignKey(Estadostransporte, models.DO_NOTHING, db_column='estadoid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transportes'


class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.TextField(unique=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    telefone = models.TextField()
    endereco = models.TextField()
    campoid = models.ForeignKey(Campos, models.DO_NOTHING, db_column='campoid', blank=True, null=True)
    cargoid = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='cargoid', blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Vinhas(models.Model):
    vinhaid = models.AutoField(primary_key=True)
    nome = models.TextField()
    castaid = models.ForeignKey(Castas, models.DO_NOTHING, db_column='castaid', blank=True, null=True)
    campoid = models.ForeignKey(Campos, models.DO_NOTHING, db_column='campoid', blank=True, null=True)
    coordenadas = models.TextField()
    dataplantacao = models.DateField(blank=True, null=True)
    hectares = models.DecimalField(max_digits=65535, decimal_places=65535)
    isactive = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vinhas'

