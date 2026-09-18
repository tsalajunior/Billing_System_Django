from django.shortcuts import render
from django.views import View
from .models import *
from django.contrib import messages


# Create your views here.
class HomeView(View):
    """
    Home view for the invoice application.
    Renders the index.html template.
    """

    template_name = "index.html"
    """
    select_related is used to optimize database queries by fetching related objects in a single query, reducing the number of database hits.
    In this case, it fetches the related 'customer' object for each invoice, which can improve performance when displaying invoice data along with customer information.
    """
    invoices = Invoice.objects.select_related("customer", "save_by").all()
    context = {"invoices": invoices}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)


class AddCustomerView(View):
    """
    View for adding a new customer.
    Renders the add_customer.html template.
    """

    template_name = "add_customer.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip_code'),
            'save_by': request.user
        }
        try:
            created = Customer.objects.create(**data)  #
            if created:
                messages.success(request, "Customer added successfully.")
            else:
                messages.error(request, "Error, try again.")
        except Exception as e:
            messages.error(request, f"Error occurred while adding customer: {str(e)}")

        return render(request, self.template_name)
