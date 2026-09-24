from django.contrib import admin
from django.utils.translation import gettext_lazy as _ 
from Invoice_app.models import Customer, Invoice, Products
from .migrations import *


admin.site.site_header = _("Invoice Management System")
admin.site.index_title = "Invoice Management System Dashboard"
admin.site.site_title = "Invoice Management System Login"

class AdminCustomer(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "address", "sex", "age", "city", "zip_code", "created_at")
    search_fields = ("name", "email", "phone_number", "city")
    list_filter = ("name", "email")

class AdminInvoice(admin.ModelAdmin):   
    list_display = ("customer", "invoice_date", "amount", "last_updated", "paid", "invoice_type")
    # search_fields = ("customer__name", "customer__email", "customer__phone_number")
    list_filter = ("paid", "invoice_type", "invoice_date")

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Products)