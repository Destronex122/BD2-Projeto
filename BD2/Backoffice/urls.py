from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path ("" , views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('userdetail/<int:userid>/', views.userdetail, name='userdetail'),
    path('users/',  views.users, name='users'),
    path('user/<int:userid>/', views.userdetail, name='user-detail'),
    path('fields/', views.fields, name='fields'),
    path('save_marker/', views.save_marker_view, name='save_marker'),
    path('save_polygon/', views.save_polygon_view, name="save_polygon"),
    path('backoffice/load_castas/', views.load_castas, name='load_castas'),
    path('vineyards/create_vineyard/', views.create_vineyard, name='create_vineyard'),
    path('update_dashboard/', views.update_dashboard, name='update_dashboard'),
    path('vineyards/delete/<int:vinhaid>/', views.delete_vineyard, name='delete_vineyard'),
    path('atualizar-producao-uvas/', views.atualizar_producao_uvas, name='atualizar_producao_uvas'),
    path('buscar-producao-uvas/', views.buscar_producao_uvas, name='buscar_producao_uvas'),
    path('load_vineyards/', views.load_vineyards, name='load_vineyards'),
    path('vineyards/get/<int:vinha_id>/', views.get_vineyard, name='get_vineyard'),
    path('vineyards/update/', views.update_vineyard, name='update_vineyard'),
    path('home/', views.backofficeIndex, name='backofficeIndex'),
    path('delivery/',  views.delivery, name='delivery'),
    path('deliverydetail/<int:idtransporte>/',  views.deliverydetail, name='deliverydetail'),
    path('harvest/',  views.harvest, name='harvest'),
    path('create-harvest/', views.create_harvest, name='create_harvest'),
    path('edit-harvest/<int:colheita_id>/', views.edit_harvest, name='edit_harvest'),
    path('inactivate-harvest/<int:colheita_id>/', views.inactivate_harvest, name='inactivate_harvest'),
    path('harvestdetail/<int:colheitaid>/', views.harvestdetail, name='harvestdetail'),
    path('edit_pesagem/<int:pesagemid>/', views.edit_pesagem, name='edit_pesagem'),
    path('add_pesagem/<int:colheitaid>/', views.add_pesagem, name='add_pesagem'),
    path('delete_pesagem/<int:pesagemid>/', views.delete_pesagem, name='delete_pesagem'),
    path('add_note_harvest/<int:colheitaid>/', views.add_note_harvest, name='add_note_harvest'),
    path('edit_note_harvest/<int:notaid>/', views.edit_note_harvest, name='edit_note'), 
    path('delete_note_harvest/<int:notaid>/', views.delete_note_harvest, name='delete_note'),
    path('vineyards/',  views.load_vineyards_view, name='vineyards'),
    path('contracts/',  views.contracts, name='contracts'),
    path('contractdetail/<int:contratoid>/', views.contractdetail, name='contractdetail'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('request/', views.request, name='request'),
    path('add_request/', views.add_request, name='add_request'),
    path('add_note_request/<int:pedidoid>/', views.add_note_request, name='add_note_request'),
    path('edit_note_request/<int:notaid>/', views.edit_note_request, name='edit_note_request'),
    path('delete_note_request/<int:notaid>/', views.delete_note_request, name='delete_note_request'),
    path('update_request/<int:pedidoid>/', views.update_request, name='update_request'),
    path('delete_request/<int:pedidoid>/', views.delete_request, name='delete_request'),
    path('requestdetail/<int:pedidoid>/', views.requestdetail, name='requestdetail'),
    path('add_item/', views.add_item, name='add_item'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('grapevariety/', views.grapevariety, name='grapevariety'),
    path('addvariety/', views.addvariety, name='addvariety'),
    path('deletevariety/<int:castaid>/', views.delete_variety, name='deletevariety'),
    path('editvariety/<int:castaid>/', views.editvariety, name='editvariety'),
    path('load_croplands/', views.load_croplands, name='load_croplands'),  
    path('get_campo_data/<int:campoid>/', views.get_campo_data, name='get_campo_data'),
    path('update_campo/<int:campoid>/', views.update_campo, name='update_campo'),
    path('delete_campo/<int:campoid>/', views.delete_campo, name='delete_campo'),
    path('payment_methods/', views.payment_methods, name='payment_methods'),
    path('addpaymentmethod/', views.add_payment_method, name='addpaymentmethod'),
    path('editpaymentmethod/<int:method_id>/', views.edit_payment_method, name='editpaymentmethod'),
    path('deletepaymentmethod/<int:method_id>/', views.delete_payment_method, name='deletepaymentmethod'),
    path('transport_states/', views.transport_states, name='transport_states'), 
    path('add_transport_state/', views.add_transport_state, name='add_transport_state'), 
    path('edit_transport_state/<int:state_id>/', views.edit_transport_state, name='edit_transport_state'),
    path('delete_transport_state/<int:state_id>/', views.delete_transport_state, name='delete_transport_state'), 
    path('receipt_status/', views.receipt_status, name='receipt_status'), 
    path('add_receipt_status/', views.add_receipt_status, name='add_receipt_status'), 
    path('edit_receipt_status/<int:status_id>/', views.edit_receipt_status, name='edit_receipt_status'),
    path('delete_receipt_status/<int:status_id>/', views.delete_receipt_status, name='delete_receipt_status'), 
    path('approved_status/', views.approved_status, name='approved_status'), 
    path('add_approved_status/', views.add_approved_status, name='add_approved_status'), 
    path('edit_approved_status/<int:approvedId>/', views.edit_approved_status, name='edit_approved_status'),
    path('delete_approved_status/<int:approvedId>/', views.delete_approved_status, name='delete_approved_status'), 
    path('settings/', views.settings, name='settings'),
    path('create_recibo/', views.create_recibo, name='create_recibo'),
    path('deactivate_recibo/<int:recibo_id>/', views.deactivate_recibo, name='deactivate_recibo'),
    path('update_recibo_status/<int:recibo_id>/pago/', views.update_recibo_status, name='update_recibo_status'),
    path('importar_campos/', views.importar_campos, name='importar_campos'),
    path('export/contract/json/<int:contratoid>/', views.export_contract_json, name='export_contract_json'),
    
]
