from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import save_marker, load_markers, load_vineyards
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.db import connection
from pymongo import MongoClient
import datetime
from .models import Casta
from .models import Users

# Conectar ao MongoDB
client = MongoClient("mongodb+srv://admin:admin@bdii22470.9hleq.mongodb.net/?retryWrites=true&w=majority&appName=BDII22470/")
db = client['Interaction_Database']  # Substituir pelo nome da base do MongoDB
collection = db['coordinates']  # Substituir pelo nome da coleção do MongoDB


# Create your views here.

@login_required
def fields(request):
    return render(request, 'fields.html')

def home(request):
    return redirect('backoffice/login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('backofficeIndex')
        else:
            messages.error(request, 'Utilizador ou password incorretos!')  # Adiciona uma mensagem de erro

    form = UserCreationForm()
    context = {'form': form}
    return render(request, 'login.html', context)

@login_required
def backofficeIndex(request):
    return render(request, 'backofficeIndex.html')

@login_required
def userdetail(request):
    return render(request, 'userdetail.html')

@login_required
def users(request):
    users = Users.objects.select_related('campoid', 'cargoid').all()
    return render(request, 'users.html', {'users': users})

@login_required
def delivery(request):
    return render(request, 'delivery.html')

@login_required
def deliverydetail(request):
    return render(request, 'deliverydetail.html')

@login_required
def harvest(request):
    return render(request, 'harvest.html')

@login_required
def harvestdetail(request):
    return render(request, 'harvestdetail.html')

@login_required
def vineyards(request):
    return render(request, 'vineyards.html')

@login_required
def contracts(request):
    return render(request, 'contracts.html')

@login_required
@csrf_exempt
@require_http_methods(['POST'])
def save_marker_view(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        save_marker(request_body)
        return JsonResponse({'message': 'Marcador salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required    
@csrf_exempt
@require_http_methods(['POST'])
def save_polygon_view(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        save_marker(request_body)
        return JsonResponse({'message': 'Polígono salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def load_markers_view(request):
    markers = load_markers(request)
    return JsonResponse(markers, safe=False)

@login_required
def load_vineyards_view(request):
    print(request)

    vineyards = load_vineyards(request)
    return JsonResponse(vineyards, safe=False)

@login_required
def requestdetail(request):
    return render(request, 'requestdetail.html')

@login_required
def contractdetail(request):
    return render(request, 'contractdetail.html')

@login_required
def request(request):
    return render(request, 'request.html')

@login_required
def grapevariety(request):
    return render(request, 'grapevariety.html')

@csrf_exempt
def addvariety(request):
    if request.method == 'POST':
        # Recupera o nome da casta
        name = request.POST.get('varietyName')

        if not name:
            return JsonResponse({'message': 'O nome da casta é obrigatório!'}, status=400)

        try:
            # Insere a casta no banco de dados usando o procedimento armazenado
            with connection.cursor() as cursor:
                cursor.execute("CALL public.inserircasta(%s);", [name])

            # Redireciona para a mesma página para ver a lista de castas atualizada
            return redirect('addvariety')  # Redireciona para a view 'addvariety'

        except Exception as e:
            print("Erro:", e)
            return JsonResponse({'message': str(e)}, status=500)

    # Se for um GET, renderiza a página com a lista de castas
    grape_varieties = Casta.objects.all()  # Busque as castas na base de dados
    return render(request, 'addvariety.html', {'grape_varieties': grape_varieties})


def save_marker(request):
    if request.method == 'POST':
        try:
            # Parse request data
            data = json.loads(request.body)  # Parseando o JSON que vem do request
            lat = data['lat']
            lng = data['lng']
            title = data['title']  # Nome do campo preenchido na modal
            description = data['description']  # Cidade preenchida na modal
            
            # Salvar no MongoDB
            mongo_data = {
                "lat": lat,
                "lng": lng,
                "title": title,
                "description": description,
                "created_at": datetime.datetime.now()
            }
            collection.insert_one(mongo_data)

            # Salvar no PostgreSQL
            coordenadas = f"Lat: {lat}, Lng: {lng}"
            morada = title #Nome do campo 
            cidade = description  # 'Cidade' vem da descrição do formulário (campos da modal)
            pais = "Portugal"  # Ajustar conforme necessário
            data_criacao = datetime.datetime.now().date()

            # Executar a stored procedure para inserir no PostgreSQL
            with connection.cursor() as cursor:
                cursor.callproc('inserircampo', [
                    None,  # p_campoid - Coloque `None` se for autogerado
                    coordenadas,  # p_coordenadas - Coordenadas formatadas
                    morada,  # p_morada - Nome do campo preenchida na modal
                    cidade,  # p_cidade - A cidade preenchida na modal
                    pais,  # p_pais - Ajustado como 'Portugal'
                    data_criacao  # p_datacriacao - Data atual
                ])

            return JsonResponse({'status': 'success', 'message': 'Campo guardado com sucesso no MongoDB e PostgreSQL.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)