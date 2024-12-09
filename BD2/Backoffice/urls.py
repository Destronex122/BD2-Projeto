from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path ("" , views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('userdetail/<int:userid>/', views.userdetail, name='userdetail'),
    path('users/',  views.users, name='users'),
    path('fields/', views.fields, name='fields'),
    path('save_marker/', views.save_marker_view, name='save_marker'),
    path('save_polygon/', views.save_polygon_view, name="save_polygon"),
    path('load_vineyards/', views.load_vineyards, name='load_vineyards'),
    path('home/', views.backofficeIndex, name='backofficeIndex'),
    path('delivery/',  views.delivery, name='delivery'),
    path('deliverydetail/',  views.deliverydetail, name='deliverydetail'),
    path('harvest/',  views.harvest, name='harvest'),
    path('harvestdetail/<int:colheitaid>/', views.harvestdetail, name='harvestdetail'),
    path('vineyards/',  views.load_vineyards_view, name='vineyards'),
    path('contracts/',  views.contracts, name='contracts'),
    path('contractdetail/<int:contratoid>/', views.contractdetail, name='contractdetail'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('request/', views.request, name='request'),
    path('requestdetail/<int:pedidoid>/', views.requestdetail, name='requestdetail'),
    path('grapevariety/', views.grapevariety, name='grapevariety'),
    path('addvariety/', views.addvariety, name='addvariety'),
    path('deletevariety/<int:castaid>/', views.delete_variety, name='deletevariety'),
    path('editvariety/<int:castaid>/', views.editvariety, name='editvariety'),
    path('mapa/', views.mapa_campos, name='mapa_campos'), 
    path('load_croplands/', views.load_croplands, name='load_croplands'),  
    path('get_campo_data/<int:campoid>/', views.get_campo_data, name='get_campo_data'),
    path('update_campo/<int:campoid>/', views.update_campo, name='update_campo'),
    path('delete_campo/<int:campoid>/', views.delete_campo, name='delete_campo'),
]
