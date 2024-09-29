from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import save_marker, load_markers, load_vineyards
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Create your views here.

def debug(request):
    return render(request, 'debug.html')

def home(request):
    return render(request, "home.html")

def login_view(request):
    return render(request, 'login.html')

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