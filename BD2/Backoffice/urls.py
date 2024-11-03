from django.urls import path
from . import views

urlpatterns = [
    path ("" , views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('debug/', views.debug, name='debug'),
    path('save_marker/', views.save_marker_view, name='save_marker'),
    path('save_polygon/', views.save_polygon_view, name="save_polygon"),
    path('load_croplands/', views.load_markers_view, name='load_markers'),
    path('load_vineyards/', views.load_vineyards_view, name='load_vineyards'),
    path('home/', views.backofficeIndex, name='backofficeIndex'),
    path('delivery/',  views.delivery, name='delivery'),
    path('harvestdetail/',  views.harvestdetail, name='harvestdetail'),
    path('vineyards/',  views.vineyards, name='vineyards'),

]
