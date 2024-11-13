from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path ("" , views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('userdetail/',  views.userdetail, name='userdetail'),
    path('users/',  views.users, name='users'),
    path('fields/', views.fields, name='fields'),
    path('save_marker/', views.save_marker_view, name='save_marker'),
    path('save_polygon/', views.save_polygon_view, name="save_polygon"),
    path('load_croplands/', views.load_markers_view, name='load_markers'),
    path('load_vineyards/', views.load_vineyards_view, name='load_vineyards'),
    path('home/', views.backofficeIndex, name='backofficeIndex'),
    path('delivery/',  views.delivery, name='delivery'),
    path('deliverydetail/',  views.deliverydetail, name='deliverydetail'),
    path('harvest/',  views.harvest, name='harvest'),
    path('harvestdetail/',  views.harvestdetail, name='harvestdetail'),
    path('vineyards/',  views.vineyards, name='vineyards'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
