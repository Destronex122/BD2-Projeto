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


class Casta(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


