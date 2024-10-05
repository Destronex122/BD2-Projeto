from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import save_marker, load_markers, load_vineyards
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def debug(request):
    return render(request, 'debug.html')

def home(request):
    return redirect('backoffice/login')

def login_view(request):

    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if  user is not None:
            login(request, user)
            return redirect('backofficeIndex')

    form = UserCreationForm()
    context = {'form':form}
    return render(request, 'login.html')

def backofficeIndex(request):
    return render(request, 'backofficeIndex.html')

def delivery(request):
    return render(request, 'delivery.html')

@csrf_exempt
@require_http_methods(['POST'])
def save_marker_view(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        save_marker(request_body)
        return JsonResponse({'message': 'Marcador salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(['POST'])
def save_polygon_view(request):
    try:
        request_body = json.loads(request.body.decode('utf-8'))
        save_marker(request_body)
        return JsonResponse({'message': 'Polígono salvo com sucesso!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def load_markers_view(request):
    markers = load_markers(request)
    return JsonResponse(markers, safe=False)

def load_vineyards_view(request):
    print(request)

    vineyards = load_vineyards(request)
    return JsonResponse(vineyards, safe=False)