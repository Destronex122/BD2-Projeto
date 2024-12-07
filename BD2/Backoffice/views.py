from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import load_vineyards
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.db import connection
from pymongo import MongoClient
from django.shortcuts import render, get_object_or_404
import datetime
from django.db.models import Max
from .models import Casta
from .models import Users,Castas, Colheitas,Vinhas,Pesagens, Pedidos, Clientes, Contratos, Campos,Transportes,Cargo
from django.utils import timezone

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
def userdetail(request, userid):
    user = get_object_or_404(Users, userid=userid)
    
    return render(request, 'userdetail.html', {'user': user})
@login_required
def users(request):
    #Filtros
    filter_name = request.GET.get('filterName', '').strip()
    filter_email = request.GET.get('filterEmail', '').strip()
    filter_cargo = request.GET.get('filterCargo', '').strip()


    users = Users.objects.select_related('campoid', 'cargoid').all()

    if filter_name:
        users = users.filter(nome__icontains=filter_name)
    if filter_email:
        users = users.filter(email__icontains=filter_email)
    if filter_cargo:
        users = users.filter(cargoid__nome__icontains=filter_cargo)

    #Cargos para a dropdown
    cargos = Cargo.objects.all()

    return render(request, 'users.html', {
        'users': users,
        'cargos':cargos,
        'filters': {
            'filterName': filter_name,
            'filterEmail': filter_email,
            'filterCargo': filter_cargo,
        },
    })

@login_required
def delivery(request):
    transporte = Transportes.objects.all()
    return render(request, 'delivery.html', {'Transportes' : transporte })

@login_required
def deliverydetail(request,transposteid):
    transporte = get_object_or_404 (Transportes, idtransposte = transposteid ) 
    return render(request, 'deliverydetail.html', {'Transportes' : transporte })

@login_required
def harvest(request):
    #Filtros
    filter_hectares = request.GET.get('filterHectares', '').strip()
    filter_casta = request.GET.get('filterCasta', '').strip()
    filter_data_inicio = request.GET.get('filterDataInicio', None)

    colheitas = Colheitas.objects.select_related('vinhaid', 'vinhaid__castaid', 'periodoid').all()
    
    if filter_hectares:
        colheitas = colheitas.filter(vinhaid__hectares__exact=filter_hectares)
    if filter_casta:
        colheitas = colheitas.filter(vinhaid__castaid__nome__icontains=filter_casta)
    if filter_data_inicio:
        colheitas = colheitas.filter(datapesagem__gte=filter_data_inicio)

    colheitas_context = []

    for colheita in colheitas:
        if colheita.terminada:
            ultima_pesagem = Pesagens.objects.filter(colheitaid=colheita).aggregate(ultima_data=Max('datadepesagem'))['ultima_data']
            data_termino = ultima_pesagem
        else:
            data_termino = "Não terminada"

        colheitas_context.append({
            'colheitaid': colheita.colheitaid, 
            'vinha_hectares': colheita.vinhaid.hectares if colheita.vinhaid else None,
            'casta_nome': colheita.vinhaid.castaid.nome if colheita.vinhaid and colheita.vinhaid.castaid else None,
            'peso_total': colheita.pesototal,
            'preco_por_tonelada': colheita.precoportonelada,
            'data_ultima_pesagem': colheita.datapesagem,
            'periodo': f"{colheita.periodoid.datainicio} a {colheita.periodoid.datafim}" if colheita.periodoid else None,
            'previsao_fim_colheita': colheita.previsaofimcolheita,
            'terminada': "Sim" if colheita.terminada else "Não",
            'data_termino': data_termino if data_termino else "Não terminada",
        })

    return render(request, 'harvest.html', {'colheitas': colheitas_context})

@login_required
def harvestdetail(request, colheitaid):
    colheita = get_object_or_404(Colheitas, colheitaid=colheitaid)

    colheita_context = {
        'vinha_nome': colheita.vinhaid.hectares if colheita.vinhaid else None,
        'casta_nome': colheita.vinhaid.castaid.nome if colheita.vinhaid and colheita.vinhaid.castaid else None,
        'peso_total': colheita.pesototal,
        'preco_por_tonelada': colheita.precoportonelada,
        'periodo': colheita.periodoid.ano,
        'data_pesagem': colheita.datapesagem,
        'previsao_fim_colheita': colheita.previsaofimcolheita,
        'terminada': "Sim" if colheita.terminada else "Não",
        'data_termino': colheita.datapesagem if colheita.terminada else "Não terminada",
    }

    return render(request, 'harvestdetail.html', {'colheita': colheita_context})


@login_required
def contracts(request):
    contratos_list = Contratos.objects.all()
    return render(request, 'contracts.html', {'contrato': contratos_list})



    

@login_required
@csrf_exempt
@require_http_methods(['POST'])
def save_marker_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        coordenadas = data.get('coordenadas')
        nome = data.get('nome')
        morada = data.get('morada')
        cidade = data.get('cidade')

        if not coordenadas or not nome or not morada or not cidade:
            return JsonResponse({'status': 'error', 'message': 'Faltando dados obrigatórios'}, status=400)

        campo = Campos.objects.create(
            coordenadas=coordenadas,  # Coordenadas como JSON ou string
            nome=nome,
            morada=morada,
            cidade=cidade,
            pais="Portugal",
            datacriacao=timezone.now()
        )

        return JsonResponse({
            'status': 'success',
            'campo': {
                'campoid': campo.campoid,
                'nome': campo.nome,
                'morada': campo.morada,
                'cidade': campo.cidade,
                'pais': campo.pais,
                'coordenadas': campo.coordenadas,
                'datacriacao': campo.datacriacao.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

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


@require_http_methods(['GET'])
def load_markers_view(request):
    try:
        # Carregar todos os campos do banco de dados
        campos = Campos.objects.all()
        markers = []

        for campo in campos:
            markers.append({
                'campoid': campo.campoid,
                'coordenadas': campo.coordenadas,
                'nome': campo.nome,
                'morada': campo.morada,
                'cidade': campo.cidade,
                'pais': campo.pais,
                'datacriacao': campo.datacriacao.strftime('%Y-%m-%d %H:%M:%S')
            })

        # Retorna os dados no formato JSON
        return JsonResponse(markers, safe=False)

    except Exception as e:
        # Se ocorrer um erro, retorna uma resposta com erro
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def load_croplands(request):
    campos = Campos.objects.all().values('campoid', 'nome', 'cidade', 'morada', 'coordenadas')  # Obtém id, nome, cidade e coordenadas
    campos_list = list(campos)  # Converte a QuerySet para lista de dicionários
    return JsonResponse({'status': 'success', 'campos': campos_list})

def mapa_campos(request):
    campos = Campos.objects.all()  # Traz os dados da BD
    return render(request, 'mapa.html', {'campos': campos})  # Passa a variável campos para o template

@login_required
def load_vineyards_view(request):
    vineyards = load_vineyards(request)
    return JsonResponse(vineyards, safe=False)

@login_required
def requestdetail(request, pedidoid):
    pedido = get_object_or_404(Pedidos, pedidoid=pedidoid)
    return render(request, 'requestdetail.html', {'pedido': pedido})

@login_required
def contractdetail(request, contratoid):
    contrato = get_object_or_404(Contratos, contratoid=contratoid)
    cliente = contrato.clienteid  
    return render(request, 'contractdetail.html', {'contrato': contrato, 'cliente': cliente})



@login_required
def request(request):
    pedidos = Pedidos.objects.all()
    users = Users.objects.all()
    clientes = Clientes.objects.all()
    return render(request, 'request.html', {
        'clientes': clientes, 
        'users': users,
        'pedidos': pedidos,  
    })

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

@csrf_exempt
@require_http_methods(['POST'])
def save_marker(request):
    try:
        data = json.loads(request.body.decode('utf-8'))  # Recebe a requisição em JSON
        coordenadas = data.get('coordenadas')
        nome = data.get('nome')
        morada = data.get('morada')
        cidade = data.get('cidade')

        # Verifique se todos os dados obrigatórios estão presentes
        if not coordenadas or not nome or not morada or not cidade:
            return JsonResponse({'status': 'error', 'message': 'Faltando dados obrigatórios'}, status=400)

        # Separando as coordenadas em lat e lng
        try:
            lat, lng = map(float, coordenadas.split(','))
            coordenadas_json = {'lat': lat, 'lng': lng}  # Salvar como JSON
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Coordenadas inválidas'}, status=400)

        # Criar um novo registro no banco de dados
        campo = Campos.objects.create(
            coordenadas=coordenadas_json,  # Salvar as coordenadas como JSON
            nome=nome,
            morada=morada,
            cidade=cidade,
            pais="Portugal",  # País por padrão
            datacriacao=timezone.now()  # Data de criação é a data e hora atual
        )

        return JsonResponse({
            'status': 'success',
            'campo': {
                'campoid': campo.campoid,
                'nome': campo.nome,
                'morada': campo.morada,
                'cidade': campo.cidade,
                'pais': campo.pais,
                'coordenadas': campo.coordenadas,  # Retorna o JSON das coordenadas
                'datacriacao': campo.datacriacao.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"Erro ao salvar marcador: {str(e)}")  # Exibe o erro para depuração
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_campo_data(request, campoid):
    try:
        campo = Campos.objects.get(pk=campoid)
        data = {
            "campoid":campo.campoid,
            "nome": campo.nome,
            "morada": campo.morada,
            "cidade": campo.cidade,
            "coordenadas": {
                "lat": campo.coordenadas.get("lat"),
                "lng": campo.coordenadas.get("lng"),
            },
        }
        return JsonResponse({"status": "success", "campo": data})
    except Campos.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Campo não encontrado"}, status=404)
    
@csrf_exempt
def update_campo(request, campoid):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            campo = Campos.objects.get(pk=campoid)

            campo.nome = data.get('nome', campo.nome)
            campo.morada = data.get('morada', campo.morada)
            campo.cidade = data.get('cidade', campo.cidade)
            campo.coordenadas = data.get('coordenadas', campo.coordenadas)
            campo.save()

            return JsonResponse({'status': 'success', 'message': 'Campo atualizado com sucesso.'})
        except Campos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Campo não encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

@csrf_exempt
def delete_campo(request, campoid):
    if request.method == 'DELETE':
        try:
            campo = Campos.objects.get(pk=campoid)
            campo.delete()
            return JsonResponse({"status": "success", "message": "Campo eliminado com sucesso."})
        except Campos.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Campo não encontrado."}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Método não permitido."}, status=405)