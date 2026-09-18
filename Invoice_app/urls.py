from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('add_customer/', views.AddCustomerView.as_view(), name='add_customer'),
    path('add_invoice/', views.AddInvoiceView.as_view(), name='add_invoice'),
]
