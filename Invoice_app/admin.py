from django.contrib import admin

from Invoice_app.models import Customer, Invoice, Products
from .migrations import *


class AdminCustomer(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number", "address", "sex", "age", "city", "zip_code", "created_at")
    search_fields = ("name", "email", "phone_number", "city")

class AdminInvoice(admin.ModelAdmin):   
    list_display = ("customer", "invoice_date", "amount", "last_updated", "paid", "invoice_type")
    # search_fields = ("customer__name", "customer__email", "customer__phone_number")
    list_filter = ("paid", "invoice_type", "invoice_date")

admin.site.register(Customer, AdminCustomer)
admin.site.register(Invoice, AdminInvoice)
admin.site.register(Products)
admin.site.site_header = "Invoice Management System"