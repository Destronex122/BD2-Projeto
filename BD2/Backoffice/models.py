from pymongo import MongoClient
from pymongo import MongoClient 
from bson.json_util import dumps

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
    
    return json_data

def load_vineyards(request):
    """
    Load vineyards from the database and return them as a list of JSON objects.
    
    Returns:
        str: A JSON string representing the list of vineyards.
    """
    vineyards_collection = db[dbcollection]
    vineyards = vineyards_collection.find({"coordinates": {"$exists": True}})
    # Convert the cursor to a list and then to JSON in one step
    json_data = dumps([vineyard for vineyard in vineyards], indent=2)
    
    return json_data


