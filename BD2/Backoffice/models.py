from pymongo import MongoClient
from pymongo import MongoClient 
from bson.json_util import dumps
from django.db import models

dbname='Interaction_Database'
dbcollection="coordinates"

client = MongoClient('mongodb+srv://admin:admin@bdii22470.9hleq.mongodb.net/?retryWrites=true&w=majority&appName=BDII22470/')
db = client[dbname]



def save_marker(request):
    markers_collection = db[dbcollection]
    markers_collection.insert_one(request)
    return

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



def load_markers(request):
    """
    Load markers from the database and return them as a list of JSON objects.
    
    Returns:
        str: A JSON string representing the list of markers.
    """
    markers_collection = db[dbcollection]
    markers = markers_collection.find({"lat": {"$exists": True}})
    
    # Convert the cursor to a list and then to JSON in one step
    json_data = dumps([marker for marker in markers], indent=2)
    print(json_data)
    
    return json_data

def load_vineyards(request):
    """
    Load vineyards from the database and return them as a list of JSON objects.
    
    Returns:
        str: A JSON string representing the list of vineyards.
    """
    vineyards_collection = db[dbcollection]
    vineyards = vineyards_collection.find({"coordinates": {"$exists": True}})
    print(vineyards)
    # Convert the cursor to a list and then to JSON in one step
    json_data = dumps([vineyard for vineyard in vineyards], indent=2)
    print(json_data)
    
    return json_data
#Modelo Cargo

class Cargo(models.Model):
    cargoid = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'cargo'


#Modelo Campos

class Campos(models.Model):
    campoid = models.IntegerField(primary_key=True)
    coordenadas = models.CharField(max_length=255)
    morada = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    datacriacao = models.DateField()

    class Meta:
        managed = False
        db_table = 'campos'

#Modelo User

class Users(models.Model):
    userid = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    nome = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    campoid = models.ForeignKey(Campos, models.DO_NOTHING, db_column='campoid', blank=True, null=True)
    cargoid = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='cargoid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

#Modelo Casta
class Casta(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

#Modelo Periodos
class Periodos(models.Model):
    periodoid = models.IntegerField(primary_key=True)
    datainicio = models.DateField()
    datafim = models.DateField()
    ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'periodos'

#Modelo Castas

class Castas(models.Model):
    castaid = models.IntegerField(primary_key=True)
    nome = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'castas'

#Modelo Vinhas
class Vinhas(models.Model):
    vinhaid = models.IntegerField(primary_key=True)
    castaid = models.ForeignKey(Castas, models.DO_NOTHING, db_column='castaid', blank=True, null=True)
    campoid = models.ForeignKey(Campos, models.DO_NOTHING, db_column='campoid', blank=True, null=True)
    coordenadas = models.CharField(max_length=255)
    dataplantacao = models.DateField(blank=True, null=True)
    hectares = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'vinhas'

#Modelo Colheitas 
class Colheitas(models.Model):
    colheitaid = models.IntegerField(primary_key=True)
    vinhaid = models.ForeignKey('Vinhas', models.DO_NOTHING, db_column='vinhaid', blank=True, null=True)
    pesototal = models.DecimalField(max_digits=65535, decimal_places=65535)
    precoportonelada = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    datapesagem = models.DateField(blank=True, null=True)
    periodoid = models.ForeignKey('Periodos', models.DO_NOTHING, db_column='periodoid', blank=True, null=True)
    previsaofimcolheita = models.DateField(blank=True, null=True)
    terminada = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'colheitas'
#Modelo Pesagens
class Pesagens(models.Model):
    pesagemid = models.AutoField(primary_key=True)  
    colheitaid = models.ForeignKey(
        'Colheitas', 
        on_delete=models.CASCADE, 
        db_column='colheitaid'
    )  
    pesobruto = models.DecimalField(max_digits=10, decimal_places=2)  
    pesoliquido = models.DecimalField(max_digits=10, decimal_places=2)  
    datadepesagem = models.DateField() 

    class Meta:
        managed = False 
        db_table = 'pesagens' 

#Modelo Estados Aprovações
class Estadosaprovacoes(models.Model):
    idaprovacao = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'estadosaprovacoes'

#Modelo Clientes
class Clientes(models.Model):
    clienteid = models.IntegerField(primary_key=True)
    isempresa = models.BooleanField()
    nif = models.IntegerField()
    contacto = models.CharField(max_length=100)
    morada = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'clientes'

#Modelo pedidos
class Pedidos(models.Model):
    pedidoid = models.IntegerField(primary_key=True)
    clienteid = models.ForeignKey(Clientes, models.DO_NOTHING, db_column='clienteid', blank=True, null=True)
    datainicio = models.DateField()
    datafim = models.DateField(blank=True, null=True)
    aprovadorid = models.ForeignKey('Users', models.DO_NOTHING, db_column='aprovadorid', blank=True, null=True)
    precoestimado = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedidos'
        
#Modelo pedidositem
class PedidosItem(models.Model):
    idpedido_item = models.IntegerField(primary_key=True)
    idpedido = models.ForeignKey(Pedidos, models.DO_NOTHING, db_column='idpedido', blank=True, null=True)
    castaid = models.ForeignKey(Castas, models.DO_NOTHING, db_column='castaid', blank=True, null=True)
    quantidade = models.DecimalField(max_digits=65535, decimal_places=65535)
    estadoaprovacaoid = models.ForeignKey(Estadosaprovacoes, models.DO_NOTHING, db_column='estadoaprovacaoid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pedidos_item'

#Modelo NotasPedidos
class NotasPedidos(models.Model):
    notaid = models.IntegerField(primary_key=True)
    pedidoid = models.ForeignKey('Pedidos', models.DO_NOTHING, db_column='pedidoid', blank=True, null=True)
    notas = models.CharField(max_length=500, blank=True, null=True)
    data = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notas_pedidos'

#Modelo Campos
class Pesagens(models.Model):
    pesagemid = models.AutoField(primary_key=True)  
    colheitaid = models.ForeignKey(
        'Colheitas', 
        on_delete=models.CASCADE, 
        db_column='colheitaid'
    )  
    pesobruto = models.DecimalField(max_digits=10, decimal_places=2)  
    pesoliquido = models.DecimalField(max_digits=10, decimal_places=2)  
    datadepesagem = models.DateField() 

    class Meta:
        managed = False 
        db_table = 'pesagens' 


#Modelo Contratos
class contratos(models.Model):
    contratoid = models.IntegerField(primary_key=True)
    clienteid = models.ForeignKey('Clientes', models.DO_NOTHING, db_column='clienteid', blank=True, null=True)
    idpedido_item = models.ForeignKey('PedidosItem', models.DO_NOTHING, db_column='idpedido_item', blank=True, null=True)
    datainicio = models.DateField(blank=True, null=True)
    datafim = models.DateField(blank=True, null=True)
    qtdeestimada = models.DecimalField(max_digits=65535, decimal_places=65535)
    precoestimada = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False