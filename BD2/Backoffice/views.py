from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import load_vineyards
from django.http import JsonResponse
from psycopg2.extras import Json
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
from .models import Users,Castas, Colheitas,Vinhas,Pesagens, Pedidos, Clientes, Contratos, Campos,Transportes,Cargo, NotasColheitas, NotasPedidos, Metodospagamento, PedidosItem, Estadostransporte, Estadosrecibo, Estadosaprovacoes, Periodos
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Value, BooleanField, Case, When, F, Q, Max
import logging
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect


# Conectar ao MongoDB
client = MongoClient("mongodb+srv://admin:admin@bdii22470.9hleq.mongodb.net/?retryWrites=true&w=majority&appName=BDII22470/")
db = client['Interaction_Database']  # Substituir pelo nome da base do MongoDB
collection = db['coordinates']  # Substituir pelo nome da coleção do MongoDB


# Create your views here.

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

def settings(request):
    return render(request, 'settings.html')

@login_required
def backofficeIndex(request):
    return render(request, 'backofficeIndex.html')

@login_required
def userdetail(request, userid):
    user = get_object_or_404(Users, userid=userid)
    cargos = Cargo.objects.all()  # Buscar todos os cargos do banco de dados
    if request.method == 'POST':
        # Atualizar os dados do usuário
        user.nome = request.POST.get('nome')
        user.email = request.POST.get('email')
        user.telefone = request.POST.get('telefone')
        user.endereco = request.POST.get('endereco')
        user.postalcode = request.POST.get('postalcode')
        user.city = request.POST.get('city')
        user.cargoid_id = request.POST.get('cargoid')  # Atualiza a ForeignKey com o ID do cargo
        user.save()
        return redirect('user-detail', userid=user.userid)

    return render(request, 'userdetail.html', {'user': user, 'cargos': cargos})

@login_required
def update_user_detail(userid, nome, email, telefone, endereco, postalcode, city, cargoid, campoid=None):
    with connection.cursor() as cursor:
        cursor.callproc("EditUserDetail", [userid, nome, email, telefone, endereco, postalcode, city, cargoid, campoid])

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

    #Campos para a dropdown
    campos = Campos.objects.all()

    if request.method == "POST":
        try:
            # Capturar dados do formulário
            username = request.POST['username']
            nome = request.POST['nome']
            email = request.POST['email']
            password = request.POST['password']  # A senha será tratada pelo trigger
            telefone = request.POST['telefone']
            endereco = request.POST['endereco']
            campoid = request.POST.get('campoid')
            cargoid = request.POST.get('cargoid')

            # Encripta a senha
            encrypted_password = make_password(password)

            # Chamar o procedimento armazenado
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL sp_inserir_user(%s, %s, %s, %s, %s, %s, %s, %s);",
                    [username, nome, email, encrypted_password, telefone, endereco, campoid, cargoid]
                )

            return JsonResponse({'message': 'Usuário adicionado com sucesso!'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'users.html', {
        'users': users,
        'cargos': cargos,
        'campos': campos,
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


#COLHEITA
@login_required
def harvest(request):
    # Obter filtros
    filter_vinha = request.GET.get('filterVinha', '').strip()
    filter_periodo_inicio = request.GET.get('filterPeriodoInicio', None)
    filter_periodo_fim = request.GET.get('filterPeriodoFim', None)
    filter_estado = request.GET.get('filterIsActive', '').strip()

    # Queryset de colheitas
    colheitas = Colheitas.objects.select_related('vinhaid', 'periodoid').all()

    # Aplicar filtros
    if filter_vinha:
        colheitas = colheitas.filter(vinhaid__nome__icontains=filter_vinha)
    if filter_periodo_inicio:
        colheitas = colheitas.filter(periodoid__datainicio__gte=filter_periodo_inicio)
    if filter_periodo_fim:
        colheitas = colheitas.filter(periodoid__datafim__lte=filter_periodo_fim)
    if filter_estado:
        if filter_estado == 'active':
            colheitas = colheitas.filter(isactive=True)
        elif filter_estado == 'inactive':
            colheitas = colheitas.filter(isactive=False)

    # Queryset de vinhas para o dropdown
    vinhas = Vinhas.objects.filter(isactive=True)

    # Adicionar informações para exibição
    colheitas_context = []
    for colheita in colheitas:
        # Buscar as pesagens associadas a essa colheita específica
        pesagens_colheita = Pesagens.objects.filter(colheitaid=colheita).order_by('-datadepesagem')
        
        # Obter a última pesagem (se houver)
        ultima_pesagem = pesagens_colheita.first()

        colheita.data_ultima_pesagem = ultima_pesagem.datadepesagem if ultima_pesagem else None

        colheitas_context.append({
            'colheitaid': colheita.colheitaid,
            'vinha_nome': colheita.vinhaid.nome if colheita.vinhaid else "Sem Vinha",
            'vinha_id': colheita.vinhaid.id if colheita.vinhaid and hasattr(colheita.vinhaid, 'id') else None,
            'peso_total': colheita.pesototal,
            'preco_por_tonelada': colheita.precoportonelada,
            'data_ultima_pesagem': colheita.data_ultima_pesagem,
            'periodo_inicio': colheita.periodoid.datainicio if colheita.periodoid else None,
            'periodo_fim': colheita.periodoid.datafim if colheita.periodoid else None,
            'previsao_fim_colheita': colheita.previsaofimcolheita,
            'isactive': colheita.isactive,
        })

    # Renderizar o template
    return render(request, 'harvest.html', {
        'colheitas': colheitas_context,
        'vinhas': vinhas,  # Passa as vinhas para o template,
        'filters': {
            'filterVinha': filter_vinha,
            'filterPeriodoInicio': filter_periodo_inicio,
            'filterPeriodoFim': filter_periodo_fim,
            'filterIsActive': filter_estado,
        },
    })


@login_required
def create_harvest(request):
    if request.method == 'POST':
        try:
            vinha_id = request.POST.get('vinhaId')
            peso_total = request.POST.get('pesoTotal')
            preco_por_tonelada = request.POST.get('precoPorTonelada')
            data_pesagem = request.POST.get('dataPesagem')
            periodo_inicio = request.POST.get('periodoInicio')
            periodo_fim = request.POST.get('periodoFim')
            periodo_ano = int(request.POST.get('periodoAno'))
            previsao_fim_colheita = request.POST.get('previsaoFimColheita')
            print(f"vinha_id: {vinha_id}")  # Verifique se o ID da vinha está sendo enviado
            print(f"data_pesagem: {data_pesagem}")
            # Chamar procedimento armazenado para criar a colheita
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_criar_colheita(
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    vinha_id,
                    peso_total,
                    preco_por_tonelada,
                    data_pesagem,
                    periodo_inicio,
                    periodo_fim,
                    periodo_ano,
                    previsao_fim_colheita
                ])

            return JsonResponse({'success': True, 'message': 'Colheita criada com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar colheita: {e}'})


@login_required
def edit_harvest(request, colheita_id):
    if request.method == 'POST':
        try:
            vinha_id = request.POST.get('vinhaId')
            peso_total = float(request.POST.get('pesoTotal'))
            preco_por_tonelada = float(request.POST.get('precoPorTonelada'))
            data_pesagem = request.POST.get('dataPesagem')
            periodo_inicio = request.POST.get('periodoInicio')
            periodo_fim = request.POST.get('periodoFim')
            periodo_ano = int(request.POST.get('periodoAno'))
            previsao_fim_colheita = request.POST.get('previsaoFimColheita')

            # Chamar procedimento armazenado para editar a colheita
            with connection.cursor() as cursor:
                cursor.execute("""
                     CALL sp_criar_colheita(
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    vinha_id if vinha_id else None,
                    peso_total,
                    preco_por_tonelada,
                    data_pesagem,
                    periodo_inicio,
                    periodo_fim,
                    periodo_ano,
                    previsao_fim_colheita
                ])

            return JsonResponse({'success': True, 'message': 'Colheita editada com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar colheita: {e}'})


@login_required
def inactivate_harvest(request, colheita_id):
    if request.method == 'POST':
        try:
            # Chamar procedimento armazenado para inativar a colheita
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_inativar_colheita(%s)
                """, [colheita_id])

            return JsonResponse({'success': True, 'message': 'Colheita inativada com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao inativar colheita: {e}'})



#DETALHE DA COLHEITA
@login_required
def harvestdetail(request, colheitaid):
    colheita = get_object_or_404(Colheitas, colheitaid=colheitaid)
    pesagens = Pesagens.objects.filter(colheitaid=colheitaid).order_by('-datadepesagem')

    rows_per_page = 5
    page_number = int(request.GET.get('page', 1))  # Obtém o número da página da URL, padrão é 1
    start_index = (page_number - 1) * rows_per_page
    end_index = start_index + rows_per_page

    paginated_pesagens = pesagens[start_index:end_index]
    total_pages = (pesagens.count() + rows_per_page - 1) // rows_per_page  # Calcula o total de páginas

    # Cria a lista de páginas
    pages = list(range(1, total_pages + 1))

    # Consultar as notas
    with connection.cursor() as cursor:
        cursor.execute("SELECT notaid, colheitaid, notas, data FROM public.notas_colheitas WHERE colheitaid = %s ORDER BY data DESC", [colheitaid])
        notas = cursor.fetchall()

    notas_list = [{"notaid": nota[0], "colheitaid": nota[1], "notas": nota[2], "data": nota[3]} for nota in notas]

    colheita_context = {
        'vinha_nome': colheita.vinhaid.hectares if colheita.vinhaid else None,
        'casta_nome': colheita.vinhaid.castaid.nome if colheita.vinhaid and colheita.vinhaid.castaid else None,
        'peso_total': colheita.pesototal,
        'preco_por_tonelada': colheita.precoportonelada,
        'periodo': colheita.periodoid.ano if colheita.periodoid else None,
        'data_pesagem': colheita.datapesagem,
        'previsao_fim_colheita': colheita.previsaofimcolheita,
        'terminada': "Sim" if colheita.terminada else "Não",
        'data_termino': colheita.datapesagem if colheita.terminada else "Não terminada",
    }

    return render(
        request,
        'harvestdetail.html',
        {
            'colheita': colheita_context,
            'pesagens': paginated_pesagens,
            'current_page': page_number,
            'pages': pages,  # Lista de páginas
            'notas': notas_list,  # Passando as notas
        },
    )


#PESAGEM
@csrf_exempt
def add_pesagem(request, colheitaid):  # Colheita ID vem do URL
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Captura os dados enviados
            peso_bruto = data.get('pesobruto')
            peso_liquido = data.get('pesoliquido')
            data_pesagem = data.get('datadepesagem')

            # Validação dos dados recebidos
            if not all([peso_bruto, peso_liquido, data_pesagem]):
                return JsonResponse({'success': False, 'message': 'Todos os campos são obrigatórios.'})

            # Chama o procedimento armazenado para adicionar a pesagem
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL sp_add_pesagem(%s, %s, %s, %s)", 
                    [colheitaid, peso_bruto, peso_liquido, data_pesagem]
                )

            return JsonResponse({'success': True})
        except Exception as e:
            # Retorna uma mensagem de erro se algo der errado
            return JsonResponse({'success': False, 'message': f'Erro ao adicionar pesagem: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def edit_pesagem(request, pesagemid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pesobruto = data.get('pesobruto')
            pesoliquido = data.get('pesoliquido')
            datadepesagem = data.get('datadepesagem')

            # Valida se todos os campos estão preenchidos
            if not all([pesobruto, pesoliquido, datadepesagem]):
                return JsonResponse({'success': False, 'message': 'Dados inválidos. Preencha todos os campos.'})

            # Chama o procedimento armazenado com CALL
            if pesagemid:  # Se um ID foi fornecido, edite
                with connection.cursor() as cursor:
                    cursor.execute(
                        "CALL sp_edit_pesagem(%s, %s, %s, %s)",
                        [pesagemid, pesobruto, pesoliquido, datadepesagem]
                    )
            else:  # Caso contrário, retorne um erro (não criar novo)
                return JsonResponse({'success': False, 'message': 'ID da pesagem inválido para edição.'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao salvar pesagem: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def delete_pesagem(request, pesagemid):
    if request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_pesagem(%s)", [pesagemid])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir a pesagem: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})



#NOTAS DA COLHEITA
@login_required
def get_notas(request, colheitaid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT notaid, colheitaid, notas, data FROM public.notas_colheitas WHERE colheitaid = %s ORDER BY data DESC", [colheitaid])
            notas = cursor.fetchall()
            # Criar um dicionário com as notas
            notas_list = [{"notaid": nota[0], "colheitaid": nota[1], "notas": nota[2], "data": nota[3]} for nota in notas]

        return JsonResponse({"notas": notas_list}, safe=False)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@login_required
def add_note_harvest(request, colheitaid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto = data.get('texto')

            if not texto:
                return JsonResponse({'success': False, 'message': 'O texto da nota não pode estar vazio.'})

            # Chama o procedimento para adicionar a nota
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_add_nota_colheita(%s, %s)",
                    [colheitaid, texto]
                )

            return JsonResponse({'success': True, 'message': 'Nota adicionada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao adicionar a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def edit_note_harvest(request, notaid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto = data.get('texto')

            if not texto:
                return JsonResponse({'success': False, 'message': 'O texto da nota não pode estar vazio.'})

            # Chama o procedimento para editar a nota
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_edit_nota_colheita(%s, %s)",  # Chama o procedimento de edição
                    [notaid, texto]
                )

            return JsonResponse({'success': True, 'message': 'Nota atualizada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

def delete_note_harvest(request, notaid):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_delete_nota_colheita(%s)",  # Procedimento de exclusão
                    [notaid]
                )
            return JsonResponse({'success': True, 'message': 'Nota excluída com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def contracts(request):
    # Filtros
    filter_number = request.GET.get('filterNumber', '').strip()
    filter_date = request.GET.get('filterDate', None)
    filter_client_nif = request.GET.get('filterClientNif', '').strip()

    contratos = Contratos.objects.filter(isactive=True)  # Apenas contratos ativos
    clientes = Clientes.objects.filter(isactive=True)
    pedidos = PedidosItem.objects.filter(isactive=True)

    if filter_number:
        contratos = contratos.filter(contratoid__icontains=filter_number)
    if filter_date:
        contratos = contratos.filter(datainicio=filter_date)
    if filter_client_nif:
        contratos = contratos.filter(clienteid__nif__icontains=filter_client_nif)

    # Verificar se é uma requisição POST para criar ou excluir contrato
    if request.method == 'POST':
        if 'deleteContract' in request.POST:
            contratoid = int(request.POST.get('deleteContract'))
            try:
                with connection.cursor() as cursor:
                    cursor.execute("CALL sp_delete_contrato(%s)", [contratoid])
                return JsonResponse({'status': 'success', 'message': 'Contrato excluído com sucesso!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro: {e}'})

        else:
            # Criar um novo contrato
            try:
                # Captura os valores enviados pelo formulário
                cliente_id = int(request.POST.get('clienteId'))
                pedido_id = int(request.POST.get('pedidoId')) if request.POST.get('pedidoId') else None
                data_inicio = request.POST.get('dataInicio')
                data_fim = request.POST.get('dataFim')
                quantidade_estimada = float(request.POST.get('quantidadeEstimada'))
                preco_estimado = float(request.POST.get('precoEstimado'))
                quantidade_final = float(request.POST.get('quantidadeFinal'))
                nome = request.POST.get('nomeContrato')

                # Verificar restrições
                if quantidade_final < 0 or quantidade_final < quantidade_estimada:
                    raise ValueError("A quantidade final deve ser maior ou igual à quantidade estimada.")

                # Valores padrão para campos opcionais
                preco_final = 0
                is_active = True

                # Chamar o procedimento armazenado
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_criarcontrato(
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, [
                        cliente_id, pedido_id, data_inicio, data_fim,
                        quantidade_estimada, preco_estimado,
                        quantidade_final, preco_final, nome, is_active
                    ])
                return JsonResponse({'status': 'success', 'message': 'Contrato criado com sucesso!'})

            except ValueError as ve:
                return JsonResponse({'status': 'error', 'message': f'Erro nos valores fornecidos: {ve}'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro: {e}'})

    # Renderizar a página de contratos
    return render(request, 'contracts.html', {
        'contrato': contratos,
        'clientes': clientes,
        'pedidos': pedidos,
        'filters': {
            'filterNumber': filter_number,
            'filterDate': filter_date,
            'filterClientNif': filter_client_nif,
        },
    })
    

@login_required    
@csrf_exempt
@require_http_methods(['POST'])
def save_polygon_view(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        save_marker_view(request_body)
        return JsonResponse({'message': 'Polígono salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def load_vineyards_view(request):
    vineyards = load_vineyards(request)
    print(vineyards)
    return render(request, 'vineyards.html', {'Vinhas': vineyards})

@login_required
def requestdetail(request, pedidoid):
    pedido = get_object_or_404(Pedidos, pedidoid=pedidoid)
    
    # Atualizar o estado do pedido_item
    if request.method == "POST" and "updateEstado" in request.POST:
        idpedido_item = int(request.POST.get("idpedido_item"))
        novo_estado = request.POST.get("novo_estado")  # Aceite ou Rejeitado
        try:
            with connection.cursor() as cursor:
                # Atualiza o estado do pedido_item
                cursor.execute("""
                    UPDATE pedidos_item
                    SET estadoaprovacaoid = (
                        SELECT idaprovacao FROM estadosaprovacoes WHERE nome = %s
                    )
                    WHERE idpedido_item = %s
                """, [novo_estado, idpedido_item])
            return JsonResponse({'status': 'success', 'message': f'Estado atualizado para "{novo_estado}" com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro: {e}'})
    
    # Recupera os itens do pedido
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                pi.idpedido_item, 
                pi.idpedido, 
                c.nome AS casta_nome, 
                pi.quantidade, 
                e.idaprovacao AS estado_id, 
                e.nome AS estado_nome
            FROM pedidos_item pi
            LEFT JOIN castas c ON pi.castaid = c.castaid
            LEFT JOIN estadosaprovacoes e ON pi.estadoaprovacaoid = e.idaprovacao
            WHERE pi.idpedido = %s
            ORDER BY pi.idpedido_item
        """, [pedidoid])
        pedido_items = cursor.fetchall()
    
    # Mapeia os dados para uma lista de dicionários
    pedido_items_list = [
        {
            "idpedido_item": item[0],
            "idpedido": item[1],
            "casta_nome": item[2],
            "quantidade": item[3],
            "estado_id": item[4],
            "estado_nome": item[5],
        }
        for item in pedido_items
    ]
    
    # Consulta as notas relacionadas ao pedido
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT notaid, pedidoid, notas, data FROM public.notas_pedidos WHERE pedidoid = %s ORDER BY data DESC",
            [pedidoid],
        )
        notas = cursor.fetchall()

    # Cria uma lista de dicionários com os dados das notas
    notas_list = [
        {"notaid": nota[0], "pedidoid": nota[1], "notas": nota[2], "data": nota[3]} for nota in notas
    ]

    # Passa os dados principais do pedido
    pedido_context = {
        'pedidoid': pedido.pedidoid,
        'clienteid': pedido.clienteid.clienteid if pedido.clienteid else None,
        'cliente_nome': pedido.clienteid if pedido.clienteid else "Cliente não especificado",
        'aprovadorid': pedido.aprovadorid.userid if pedido.aprovadorid else None,
        'aprovador_nome': pedido.aprovadorid.nome if pedido.aprovadorid else "Aprovador não especificado",
        'datainicio': pedido.datainicio,
        'datafim': pedido.datafim,
        'precoestimado': pedido.precoestimado,
    }
    
    return render(request, 'requestdetail.html', {
        'pedido': pedido_context,
        'notas': notas_list,
        'pedido_items': pedido_items_list,
    })


# @login_required
@login_required
def add_note_request(request, pedidoid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto = data.get('texto')

            if not texto:
                return JsonResponse({'success': False, 'message': 'O texto da nota não pode estar vazio.'})

            # Chama o procedimento para adicionar a nota
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_add_nota_pedido(%s, %s::text)",
                    [pedidoid, texto]
                )

            return JsonResponse({'success': True, 'message': 'Nota adicionada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao adicionar a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def edit_note_request(request, notaid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto = data.get('texto')

            if not texto:
                return JsonResponse({'success': False, 'message': 'O texto da nota não pode estar vazio.'})

            # Chama o procedimento para editar a nota
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_edit_nota_pedido(%s, %s)",  # Chama o procedimento de edição
                    [int(notaid), str(texto)]  # Certifique-se de passar os tipos corretos
                )

            return JsonResponse({'success': True, 'message': 'Nota atualizada com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

def delete_note_request(request, notaid):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL public.sp_delete_nota_pedido(%s)",  # Procedimento de exclusão
                    [notaid]
                )
            return JsonResponse({'success': True, 'message': 'Nota excluída com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir a nota: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def contractdetail(request, contratoid):
    contrato = get_object_or_404(Contratos, contratoid=contratoid)
    cliente = contrato.clienteid  
    return render(request, 'contractdetail.html', {'contrato': contrato, 'cliente': cliente})


@login_required
def request(request):
    # Filters
    filter_pedido = request.GET.get('filterPedido', '').strip()
    filter_data_inicio = request.GET.get('filterDataInicio', None)
    filter_data_fim = request.GET.get('filterDataFim', None)

    # Queryset
    pedidos = Pedidos.objects.all()
    users = Users.objects.all()
    clientes = Clientes.objects.all()

    # Apply filters
    if filter_pedido:
        pedidos = pedidos.filter(pedidoid__icontains=filter_pedido)
    if filter_data_inicio:
        pedidos = pedidos.filter(datainicio__gte=filter_data_inicio)
    if filter_data_fim:
        pedidos = pedidos.filter(datafim__lte=filter_data_fim)

    # Pagination
    rows_per_page = 5
    page_number = int(request.GET.get('page', 1))  # Default page is 1 if not provided
    total_items = pedidos.count()
    total_pages = (total_items + rows_per_page - 1) // rows_per_page

    # Paginated results
    start_index = (page_number - 1) * rows_per_page
    end_index = start_index + rows_per_page
    paginated_pedidos = pedidos[start_index:end_index]

    if request.method == 'POST':
        try:
            # Capturar os dados enviados pelo formulário
            aprovador_id = int(request.POST.get('aprovadorid'))
            nome = request.POST.get('newNome')
            data_inicio = request.POST.get('newDataInicio')
            data_fim = request.POST.get('newDataFim')
            preco_estimado = float(request.POST.get('newPrecoEstimado'))
            is_active = True  # Por padrão, o pedido começa ativo

            # Chamar o procedimento armazenado
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_inserirpedido(
                        %s, %s, %s, %s, %s, %s
                    )
                """, [
                    nome,
                    data_inicio,
                    data_fim,
                    aprovador_id,
                    preco_estimado,
                    is_active
                ])
            
            return JsonResponse({'success': True, 'message': 'Pedido criado com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ocorreu um erro: {e}'})

    return render(request, 'request.html', {
        'clientes': clientes,
        'users': users,
        'pedidos': paginated_pedidos,  # Pass only paginated results
        'filters': {
            'filterPedido': filter_pedido,
            'filterDataInicio': filter_data_inicio,
            'filterDataFim': filter_data_fim,
        },
        'total_pages': total_pages,  # Pass the total number of pages
        'current_page': page_number,  # Pass the current page
        'pages': range(1, total_pages + 1),  # Pass the range of pages
    })


@csrf_exempt
def add_request(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            clienteid = data.get('clienteid')
            aprovadorid = data.get('aprovadorid')
            nome = data.get('nome')
            datainicio = data.get('datainicio')
            datafim = data.get('datafim')
            precoestimado = data.get('precoestimado')

            # Ensure IDs are passed as integers
            clienteid = int(clienteid) if clienteid else None
            aprovadorid = int(aprovadorid) if aprovadorid else None

            # Call the stored procedure
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL add_pedido(%s, %s, %s, %s, %s, %s)", 
                    [clienteid, aprovadorid, nome, datainicio, datafim, precoestimado]
                )

            return JsonResponse({'success': True, 'message': 'Pedido adicionado com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao adicionar pedido: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método inválido'})


def update_request(request, pedidoid):
    if request.method == "POST":
        nome = request.POST.get("nome")
        clienteid = request.POST.get("clienteid")
        aprovadorid = request.POST.get("aprovadorid")
        datainicio = request.POST.get("datainicio")
        datafim = request.POST.get("datafim")
        precoestimado = request.POST.get("precoestimado")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL update_pedido(%s, %s, %s, %s, %s, %s)",
                    [pedidoid, clienteid, aprovadorid, nome, datainicio, datafim, precoestimado]
                )
            return redirect('/request')
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

def delete_request(request, pedidoid):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL delete_pedido(%s)", [pedidoid])
            return redirect('/request')
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Método inválido.'})

#CASTAS
def grapevariety(request):
    # Obtém os filtros
    filter_grapevariety = request.GET.get('filter_grapevariety', '').strip()
    status_filter = request.GET.get('status', 'all')  # Padrão: mostrar ativos

    # Consulta base com anotação
    grapevarieties = Castas.objects.annotate(
        isactive_cleaned=Coalesce('isactive', Value(False), output_field=BooleanField())
    ).order_by('nome')

    # Filtros de status
    if status_filter == 'active':
        grapevarieties = grapevarieties.filter(isactive_cleaned=True)
    elif status_filter == 'inactive':
        grapevarieties = grapevarieties.filter(isactive_cleaned=False)

    # Filtro pelo nome
    if filter_grapevariety:
        grapevarieties = grapevarieties.filter(nome__icontains=filter_grapevariety)

    return render(request, 'grapevariety.html', {
        'castas': grapevarieties,
        'filters': {
            'filter_grapevariety': filter_grapevariety,
            'status': status_filter,
        },
    })


@csrf_exempt
def addvariety(request):
    if request.method == 'POST':
        try:
            # Lê o corpo da requisição e decodifica o JSON
            data = json.loads(request.body)
            nome = data.get('varietyName', '').strip()

            # Validação do nome
            if not nome:
                return JsonResponse({'success': False, 'message': 'Nome inválido.'})

            # Verifica se a casta já existe (case insensitive)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM castas WHERE LOWER(nome) = LOWER(%s)", [nome])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Essa casta já existe.'})

            # Chama o procedimento armazenado para inserir a casta
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_insert_casta(%s, %s)", [nome, None])  # None para o OUT parameter
                cursor.execute("SELECT currval('castas_castaid_seq')")  # Recupera o último ID gerado
                new_castaid = cursor.fetchone()[0]

            return JsonResponse({'success': True, 'id': new_castaid, 'nome': nome})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato de dados inválido.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar a casta: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_variety(request, castaid):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_casta(%s)", [castaid])
            # Retorne o estado atualizado da casta
            return JsonResponse({'success': True, 'castaid': castaid, 'is_active': False})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao inativar a casta: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

logger = logging.getLogger(__name__)
@login_required
def editvariety(request, castaid):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            nome = body.get('varietyName', '').strip()

            if not nome:
                return JsonResponse({'success': False, 'message': 'O nome da casta é inválido.'})

            with connection.cursor() as cursor:
                cursor.execute("CALL sp_update_casta(%s, %s)", [castaid, nome])

            # Resposta de sucesso
            response = {'success': True, 'id': castaid, 'nome': nome}
            logger.info(f"Resposta editvariety: {response}")  # Log de sucesso
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato de dados inválido.'})

        except Exception as e:
            error_message = str(e)

            # Verifica se o erro é relacionado a duplicação de chave única
            if "duplicate key value violates unique constraint" in error_message:
                return JsonResponse({'success': False, 'message': 'Essa casta já existe.'})

            logger.error(f"Erro ao editar a casta: {error_message}")  # Log do erro
            return JsonResponse({'success': False, 'message': f'Erro ao editar a casta: {error_message}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})



#CAMPOS
@login_required
def fields(request):
    return render(request, 'fields.html')    


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
        
        # Validação das coordenadas
        try:
            if isinstance(coordenadas, dict):
                lat = float(coordenadas.get("lat"))
                lng = float(coordenadas.get("lng"))
                coordenadas_json = {"lat": lat, "lng": lng}  # Garante formato JSON válido
            else:
                raise ValueError("Formato inválido para coordenadas")
        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'message': f'Coordenadas inválidas: {str(e)}'}, status=400)

        campo = Campos.objects.create(
            coordenadas=coordenadas_json,  # Coordenadas como JSON ou string
            nome=nome,
            morada=morada,
            cidade=cidade,
            pais=pais,
            datacriacao=timezone.now(),
            isactive=True
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
                'datacriacao': campo.datacriacao.strftime('%Y-%m-%d %H:%M:%S'),
                'isactive': campo.isactive
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(['GET'])
def load_markers_view(request):
    try:
        # Carregar todos os campos do banco de dados
        campos = Campos.objects.all()
        markers = []

        for campo in campos:
            try:
                coordenadas = json.loads(campo.coordenadas) if isinstance(campo.coordenadas, str) else campo.coordenadas
            except (ValueError, TypeError):
                coordenadas = None  # Coordenadas inválidas ou ausentes

            if coordenadas and "lat" in coordenadas and "lng" in coordenadas:
                markers.append({
                    'campoid': campo.campoid,
                    'coordenadas': coordenadas,  # Agora como objeto JSON
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
    status_filter = request.GET.get('status', '')  # Recebe o filtro da query string
    name_filter = request.GET.get('name', '').strip().lower()
    city_filter = request.GET.get('cidade', '').strip().lower()

    if status_filter == 'active':
        campos = Campos.objects.filter(isactive=True)
    elif status_filter == 'inactive':
        campos = Campos.objects.filter(isactive=False)
    else:
        campos = Campos.objects.all()

    if name_filter:
        campos = campos.filter(nome__icontains=name_filter) | campos.filter(cidade__icontains=city_filter)

    campos = campos.values(
        'campoid', 'nome', 'cidade', 'morada', 'pais', 'coordenadas', 'isactive'
    ).order_by('nome')

    campos_list = []
    for campo in campos:
        try:
            campo['coordenadas'] = campo['coordenadas']  # Decodificar JSON
        except (ValueError, TypeError):
            campo['coordenadas'] = None  # Define como None se inválido
        
        campos_list.append(campo)

    return JsonResponse({'status': 'success', 'campos': campos_list})


def get_campo_data(request, campoid):
    try:
        campo = Campos.objects.get(pk=campoid)
        # Decodificar coordenadas se forem armazenadas como string JSON
        try:
            coordenadas = json.loads(campo.coordenadas) if isinstance(campo.coordenadas, str) else campo.coordenadas
        except (TypeError, ValueError):
            coordenadas = None
        data = {
            "campoid":campo.campoid,
            "nome": campo.nome,
            "morada": campo.morada,
            "cidade": campo.cidade,
            "pais": campo.pais,
            "coordenadas": coordenadas if coordenadas else {"lat": None, "lng": None},
        }
        return JsonResponse({"status": "success", "campo": data})
    except Campos.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Campo não encontrado"}, status=404)
    except Exception as e:
        print(f"Erro ao buscar campo: {e}")  # Log para depuração
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(['PUT'])
def update_campo(request, campoid):
    try:
        data = json.loads(request.body.decode('utf-8'))

        # Obter dados enviados pelo cliente
        nome = data.get('nome', '').strip()
        morada = data.get('morada', '').strip()
        cidade = data.get('cidade', '').strip()
        pais = data.get('pais', '').strip()
        coordenadas = data.get('coordenadas', None)

        # Validar dados obrigatórios
        if not nome or not morada or not cidade or not pais or not coordenadas:
            return JsonResponse({'status': 'error', 'message': 'Faltando dados obrigatórios.'}, status=400)
        
        try:
            coordenadas_json = json.dumps(coordenadas)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Coordenadas inválidas.'}, status=400)

        # Chamar o procedimento armazenado no banco de dados
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL sp_update_campo(%s, %s, %s, %s, %s, %s)",
                     [int(campoid), str(coordenadas_json), str(nome), str(morada), str(cidade), str(pais)]
                )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro ao executar procedimento: {str(e)}'}, status=500)

        # Retornar sucesso
        return JsonResponse({'status': 'success', 'message': 'Campo atualizado com sucesso.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Erro ao decodificar JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erro inesperado: {str(e)}'}, status=500)
    
@csrf_exempt
def delete_campo(request, campoid):
    if request.method == 'POST':  # Alterado para POST
        try:
            # Chamar o procedimento armazenado para inativar o campo
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_campo(%s)", [campoid])

            # Retorno de sucesso
            return JsonResponse({"status": "success", "message": "Campo inativado com sucesso."})

        except Exception as e:
            # Captura exceções e retorna erro
            print(f"Erro ao inativar campo: {str(e)}")  # Log para depuração
            if "não encontrado" in str(e).lower():
                return JsonResponse({"status": "error", "message": "Campo não encontrado."}, status=404)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Retorno para métodos não permitidos
    return JsonResponse({"status": "error", "message": "Método não permitido."}, status=405)


#MÉTODOS DE PAGAMENTO
def payment_methods(request):
    # Obtém os filtros
    filter_method = request.GET.get('filter_method', '').strip()

    # Ordena os métodos de pagamento por nome
    methods = Metodospagamento.objects.all().order_by('nome')

    # Filtrar pelo nome do método, se fornecido
    if filter_method:
        methods = methods.filter(nome__icontains=filter_method)

    # Renderiza a página com os métodos de pagamento
    return render(request, 'payment_methods.html', {
        'metodos': methods,
        'filters': {
            'filter_method': filter_method,
        },
    })

@csrf_exempt
def add_payment_method(request):
    if request.method == 'POST':
        try:
            # Lê os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Verifica se o nome é válido
            if not nome:
                return JsonResponse({'success': False, 'message': 'Nome inválido.'})

            # Verifica se já existe um método com o mesmo nome (case insensitive)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM metodospagamento WHERE LOWER(nome) = LOWER(%s)", [nome])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Esse método já existe.'})

            # Chama o procedimento armazenado para inserir o método
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_insert_metodo(%s, %s)", [nome, None])
                cursor.execute("SELECT currval('metodospagamento_idmetodopagamento_seq')")
                new_method_id = cursor.fetchone()[0]

            return JsonResponse({'success': True, 'id': new_method_id, 'nome': nome})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato de dados inválido.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar o método: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_payment_method(request, method_id):
    if request.method == 'POST':
        try:
            # Chama o procedimento armazenado para excluir o método
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_metodo(%s)", [method_id])
            return JsonResponse({'success': True, 'method_id': method_id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir o método: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def edit_payment_method(request, method_id):
    if request.method == 'POST':
        try:
            # Lê os dados enviados pelo cliente
            body = json.loads(request.body)
            nome = body.get('nome', '').strip()

            # Verifica se o nome é válido
            if not nome:
                return JsonResponse({'success': False, 'message': 'O nome do método é inválido.'})

            # Chama o procedimento armazenado para atualizar o método
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_update_metodo(%s, %s)", [method_id, nome])

            response = {'success': True, 'id': method_id, 'nome': nome}
            logger.info(f"Resposta edit_payment_method: {response}")
            return JsonResponse(response)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato de dados inválido.'})
        except Exception as e:
            error_message = str(e)
            if "duplicate key value violates unique constraint" in error_message:
                return JsonResponse({'success': False, 'message': 'Esse método já existe.'})
            logger.error(f"Erro ao editar o método: {error_message}")
            return JsonResponse({'success': False, 'message': f'Erro ao editar o método: {error_message}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


#ESTADO DO TRANSPORTE
@login_required
def transport_states(request):
    # Obtém os dados do banco
    states = Estadostransporte.objects.all().order_by('nome')

    # Filtro (opcional)
    filter_state = request.GET.get('filter_method', '').strip()
    if filter_state:
        states = states.filter(nome__icontains=filter_state)

    # Renderiza o template com os dados
    return render(request, 'transport_states.html', {
        'estados': states,  # Certifique-se de que 'estados' é a variável usada no template
    })

@csrf_exempt
def add_transport_state(request):
    if request.method == 'POST':
        try:
            # Lê os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Verifica se o nome é válido
            if not nome:
                return JsonResponse({'success': False, 'message': 'Nome inválido.'})

            # Verifica se já existe um estado com o mesmo nome (case insensitive)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM estadostransporte WHERE LOWER(nome) = LOWER(%s)", [nome])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Esse estado já existe.'})

            # Chama a procedure para inserir o estado e retorna o ID
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_insert_estadotransporte(%s, %s)", [nome, None])
                cursor.execute("SELECT currval('estadostransporte_idestado_seq')")
                new_id = cursor.fetchone()[0]  # Obtém o ID retornado pelo OUT parameter

            return JsonResponse({'success': True, 'id': new_id, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def edit_transport_state(request, state_id):
    if request.method == 'POST':
        try:
            # Obtém os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Valida o nome do estado
            if not nome:
                return JsonResponse({'success': False, 'message': 'O nome do estado é obrigatório.'})

            # Atualiza o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_update_estadotransporte(%s, %s)", [state_id, nome])

            return JsonResponse({'success': True, 'id': state_id, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar o estado: {str(e)}'})

        except Exception as e:
            error_message = str(e)
            if "duplicate key value violates unique constraint" in error_message:
                return JsonResponse({'success': False, 'message': 'Esse método já existe.'})
            logger.error(f"Erro ao editar o método: {error_message}")
            return JsonResponse({'success': False, 'message': f'Erro ao editar o método: {error_message}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_transport_state(request, state_id):
    if request.method == 'POST':
        try:
            # Exclui o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_estadotransporte(%s)", [state_id])
            return JsonResponse({'success': True, 'state_id': state_id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


#ESTADO DO RECIBO
@login_required
def receipt_status(request):
    # Obtém os dados do banco
    states = Estadosrecibo.objects.all().order_by('nome')

    # Filtro (opcional)
    filter_state = request.GET.get('filter_method', '').strip()
    if filter_state:
        states = states.filter(nome__icontains=filter_state)

    # Renderiza o template com os dados
    return render(request, 'receipt_status.html', {
        'estados': states,  # Certifique-se de que 'estados' é a variável usada no template
    })

@csrf_exempt
def add_receipt_status(request):
    if request.method == 'POST':
        try:
            # Lê os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Verifica se o nome é válido
            if not nome:
                return JsonResponse({'success': False, 'message': 'Nome inválido.'})

            # Verifica se já existe um estado com o mesmo nome (case insensitive)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM estadosrecibo WHERE LOWER(nome) = LOWER(%s)", [nome])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Esse estado já existe.'})

            # Chama a procedure para inserir o estado e retorna o ID
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_insert_estadorecibo(%s, %s)", [nome, None])
                cursor.execute("SELECT currval('estadosrecibo_idestado_seq')")
                new_id = cursor.fetchone()[0]  # Obtém o ID retornado pelo OUT parameter

            return JsonResponse({'success': True, 'id': new_id, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def edit_receipt_status(request, status_id):
    if request.method == 'POST':
        try:
            # Obtém os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Valida o nome do estado
            if not nome:
                return JsonResponse({'success': False, 'message': 'O nome do estado é obrigatório.'})

            # Atualiza o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_update_estadorecibo(%s, %s)", [status_id, nome])

            return JsonResponse({'success': True, 'id': status_id, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar o estado: {str(e)}'})

        except Exception as e:
            error_message = str(e)
            if "duplicate key value violates unique constraint" in error_message:
                return JsonResponse({'success': False, 'message': 'Esse método já existe.'})
            logger.error(f"Erro ao editar o método: {error_message}")
            return JsonResponse({'success': False, 'message': f'Erro ao editar o método: {error_message}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_receipt_status(request, status_id):
    if request.method == 'POST':
        try:
            # Exclui o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_estadorecibo(%s)", [status_id])
            return JsonResponse({'success': True, 'status_id': status_id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao excluir o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


#ESTADO DA APROVAÇÃO
@login_required
def approved_status(request):
    # Obtém os dados do banco
    states = Estadosaprovacoes.objects.all().order_by('nome')

    # Filtro (opcional)
    filter_state = request.GET.get('filter_method', '').strip()
    if filter_state:
        states = states.filter(nome__icontains=filter_state)

    # Renderiza o template com os dados
    return render(request, 'approved_status.html', {
        'estados': states,  # Certifique-se de que 'estados' é a variável usada no template
    })

@csrf_exempt
def add_approved_status(request):
    if request.method == 'POST':
        try:
            # Lê os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Verifica se o nome é válido
            if not nome:
                return JsonResponse({'success': False, 'message': 'Nome inválido.'})

            # Verifica se já existe um estado com o mesmo nome (case insensitive)
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM estadosaprovacoes WHERE LOWER(nome) = LOWER(%s)", [nome])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'success': False, 'message': 'Esse estado já existe.'})

            # Chama a procedure para inserir o estado e retorna o ID
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_insert_estadoaprovacoes(%s, %s)", [nome, None])
                cursor.execute("SELECT currval('estadosaprovacoes_idaprovacao_seq')")
                new_id = cursor.fetchone()[0]  # Obtém o ID retornado pelo OUT parameter

            return JsonResponse({'success': True, 'id': new_id, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao criar o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})


@login_required
def edit_approved_status(request, approvedId):
    if request.method == 'POST':
        try:
            # Obtém os dados enviados pelo cliente
            data = json.loads(request.body)
            nome = data.get('nome', '').strip()

            # Valida o nome do estado
            if not nome:
                return JsonResponse({'success': False, 'message': 'O nome do estado é obrigatório.'})

            # Atualiza o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_update_estadoaprovacoes(%s, %s)", [approvedId, nome])

            return JsonResponse({'success': True, 'id': approvedId, 'nome': nome})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao editar o estado: {str(e)}'})

        except Exception as e:
            error_message = str(e)
            if "duplicate key value violates unique constraint" in error_message:
                return JsonResponse({'success': False, 'message': 'Esse método já existe.'})
            logger.error(f"Erro ao editar o método: {error_message}")
            return JsonResponse({'success': False, 'message': f'Erro ao editar o método: {error_message}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

@login_required
def delete_approved_status(request, approvedId):
    if request.method == 'POST':
        try:
            # Exclui o estado usando a stored procedure
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_delete_estadoaprovacoes(%s)", [approvedId])
            return JsonResponse({'success': True, 'approvedId': approvedId})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao eliminar o estado: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido.'})

def load_castas(request):
    castas = Castas.objects.all().values('castaid', 'nome')
    return JsonResponse(list(castas), safe=False)

@login_required
def create_vineyard(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Obter a instância da Casta
            casta = Castas.objects.get(pk=data.get('casta'))

            # Obter a instância do Campo (Quinta) - você precisará passar o campoId de alguma forma
            campo = Campos.objects.get(pk=data.get('campoid'))  # Substitua 'campoid' pelo nome correto do campo

            # Criar a nova vinha
            vinha = Vinhas.objects.create(
                nome=data.get('nome'),
                castaid=casta,
                campoid=campo,
                coordenadas=data.get('coordinates'), # Ajuste conforme a estrutura do seu modelo para coordenadas
                dataplantacao=data.get('dataplantacao'),
                hectares=data.get('hectares'),
                isactive=True  # Ou defina como você preferir
            )

            return JsonResponse({'status': 'success', 'vinhaid': vinha.vinhaid})
        except Castas.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Casta não encontrada'}, status=400)
        except Campos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Campo (Quinta) não encontrado'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=405)
    
@require_http_methods(["PUT"])
@csrf_protect
def update_vineyard(request, vinha_id):
    try:
        vinha = Vinhas.objects.get(pk=vinha_id)
        data = json.loads(request.body)

        vinha.nome = data.get('nome')
        vinha.dataplantacao = data.get('dataplantacao')
        vinha.hectares = data.get('hectares')

        # Obter a instância da Casta, se fornecida
        if 'casta' in data:
            casta = Castas.objects.get(pk=data.get('casta'))
            vinha.castaid = casta

        vinha.save()
        return JsonResponse({'status': 'success'})
    except Vinhas.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Vinha não encontrada'}, status=404)
    except Castas.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Casta não encontrada'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)