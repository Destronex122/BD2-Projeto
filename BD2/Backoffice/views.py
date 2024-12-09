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

    #Filtros
    filter_number = request.GET.get('filterNumber', '').strip()
    filter_date = request.GET.get('filterDate', None)
    filter_state = request.GET.get('filterState', '').strip()

    transporte = Transportes.objects.all()

    if filter_number:
        transporte = transporte.filter(idtransporte__icontains=filter_number)
    if filter_date:
        transporte = transporte.filter(data=filter_date)
    if filter_state:
        transporte = transporte.filter(estadoid__nome__icontains=filter_state)

    return render(request, 'delivery.html', {
        'Transportes': transporte,
        'filters': {
            'filterNumber': filter_number,
            'filterDate': filter_date,
            'filterState': filter_state,
        },
    })

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

    #Filtros
    filter_number = request.GET.get('filterNumber', '').strip()
    filter_date = request.GET.get('filterDate', None)
    filter_client_nif = request.GET.get('filterClientNif', '').strip()

    contratos = Contratos.objects.all()

    if filter_number:
        contratos = contratos.filter(contratoid__icontains=filter_number)
    if filter_date:
        contratos = contratos.filter(datainicio=filter_date)
    if filter_client_nif:
        contratos = contratos.filter(clienteid__nif__icontains=filter_client_nif)

    return render(request, 'contracts.html', {
        'contrato': contratos,
        'filters': {
            'filterNumber': filter_number,
            'filterDate': filter_date,
            'filterClientNif': filter_client_nif,
        },
    })


    

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
        pais = data.get('pais')

        if not coordenadas or not nome or not morada or not cidade:
            return JsonResponse({'status': 'error', 'message': 'Faltando dados obrigatórios'}, status=400)

        campo = Campos.objects.create(
            coordenadas=coordenadas,  # Coordenadas como JSON ou string
            nome=nome,
            morada=morada,
            cidade=cidade,
            pais=pais,
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
    campos = Campos.objects.all().values('campoid', 'nome', 'cidade', 'morada', 'pais', 'coordenadas').order_by('nome')  # Obtém id, nome, cidade, pais e coordenadas
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
    #Filtros
    filter_pedido = request.GET.get('filterPedido', '').strip()
    filter_data_inicio = request.GET.get('filterDataInicio', None)
    filter_data_fim = request.GET.get('filterDataFim', None)

    pedidos = Pedidos.objects.all()
    users = Users.objects.all()
    clientes = Clientes.objects.all()

    if filter_pedido:
        pedidos = pedidos.filter(pedidoid__icontains=filter_pedido)
    if filter_data_inicio:
        pedidos = pedidos.filter(datainicio__gte=filter_data_inicio)
    if filter_data_fim:
        pedidos = pedidos.filter(datafim__lte=filter_data_fim)

    return render(request, 'request.html', {
        'clientes': clientes, 
        'users': users,
        'pedidos': pedidos, 
        'filters': {
            'filterPedido': filter_pedido,
            'filterDataInicio': filter_data_inicio,
            'filterDataFim': filter_data_fim,
        }, 
    })

def grapevariety(request):
    # Obtendo o filtro da query string
    filter_grapevariety = request.GET.get('filter_grapevariety', '').strip()

    # Buscando todos os objetos Castas
    grapevarieties = Castas.objects.all().order_by('nome')

    # Aplicando o filtro, se necessário
    if filter_grapevariety:
        grapevarieties = grapevarieties.filter(nome__icontains=filter_grapevariety)

    # Renderizando o template com o contexto
    return render(request, 'grapevariety.html', {
        'castas': grapevarieties,  # Passando os dados para o template
        'filters': {
            'filter_grapevariety': filter_grapevariety
        },
    })

@csrf_exempt
def addvariety(request):
    if request.method == 'POST':
        nome = request.POST.get('varietyName', '').strip()
        if nome:
            # Cria a nova casta
            new_variety = Castas.objects.create(nome=nome)
            # Retorna a nova casta como resposta JSON
            return JsonResponse({'success': True, 'id': new_variety.castaid, 'nome': new_variety.nome})
        return JsonResponse({'success': False, 'message': 'Nome inválido.'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_variety(request, castaid):
    if request.method == 'POST':
        casta = get_object_or_404(Castas, castaid=castaid)
        casta.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def editvariety(request, castaid):
    if request.method == 'POST':
        casta = get_object_or_404(Castas, castaid=castaid)
        nome = request.POST.get('varietyName', '').strip()
        if nome:
            casta.nome = nome
            casta.save()
            return JsonResponse({'success': True, 'id': casta.castaid, 'nome': casta.nome})
        return JsonResponse({'success': False, 'message': 'Nome inválido.'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@csrf_exempt
@require_http_methods(['POST'])
def save_marker(request):
    try:
        data = json.loads(request.body.decode('utf-8'))  # Recebe a requisição em JSON
        coordenadas = data.get('coordenadas')
        nome = data.get('nome')
        morada = data.get('morada')
        cidade = data.get('cidade')
        pais = data.get('pais')

        # Verifique se todos os dados obrigatórios estão presentes
        if not coordenadas or not nome or not morada or not cidade or not pais:
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
            pais=pais, 
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
            "pais": campo.pais,
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
            campo.pais = data.get('pais', campo.pais)
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

