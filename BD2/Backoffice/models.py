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

def save_polygon(request):
    markers_collection = db[dbcollection]
    markers_collection.insert_one(request)
    return


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