from django.http import request
from django.shortcuts import render
from django.views import View
from .models import *
from django.contrib import messages
from django.db import transaction
from .utils import pagination


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
        items = pagination(request, self.invoices)  # Paginate the invoices
        self.context["invoices"] = items  # Update the context with paginated invoices
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        # modify
        if request.POST.get("id_modified"):
            paid = request.POST.get("modified")
            try:
                obj = Invoice.objects.get(id=request.POST.get("id_modified"))
                if paid == "True":
                    obj.paid = True
                else:
                    obj.paid = False
                obj.save()
                messages.success(request, "Chnages made successfully.")
            except Exception as e:
                messages.error(request, f"Sorry, an error has occured: {e}")

        # deleting
        if request.POST.get("id_supprimer"):
            try:
                obj = Invoice.objects.get(pk=request.POST.get("id_supprimer"))
                obj.delete()
                messages.success(request, "Deletion was successful.")
            except Exception as e:
                messages.error(request, f"Sorry, an error has occured: {e}")
                
        # placed here to update the displayed data
        items = pagination(request, self.invoices)  # Paginate the invoices
        self.context["invoices"] = items  # Update the context with paginated invoices
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
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "phone_number": request.POST.get("phone"),
            "sex": request.POST.get("sex"),
            "age": request.POST.get("age"),
            "address": request.POST.get("address"),
            "city": request.POST.get("city"),
            "zip_code": request.POST.get("zip_code"),
            "save_by": request.user,
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


class AddInvoiceView(View):
    """
    View for adding a new invoice.
    Renders the add_invoice.html template.
    """

    template_name = "add_invoice.html"

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.select_related("save_by").all()
        return render(request, self.template_name, {"customers": customers})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        customers = Customer.objects.select_related("save_by").all()
        context = {"customers": customers}

        items = []
        try:
            with transaction.atomic():
                customer = request.POST.get("customer")
                invoice_type = request.POST.get("invoice_type")
                articles = request.POST.getlist("article")
                quantities = request.POST.getlist("qty")
                units = request.POST.getlist("unit_price")
                total_a = request.POST.getlist("total_price-a")
                total = request.POST.get("total_price")
                comments = request.POST.get("comments")

                if not articles:
                    messages.error(request, "Please add at least one article.")
                    return render(request, self.template_name, context)

                data = {
                    "customer_id": customer,
                    "save_by": request.user,
                    "invoice_type": invoice_type,
                    "amount": float(total) if total else 0.0,
                    "comments": comments,
                }

                invoice = Invoice.objects.create(**data)

                for index, article in enumerate(articles):
                    if index < len(quantities) and index < len(units):
                        item = Products(
                            invoice_id=invoice.id,
                            name=article,
                            quantity=(
                                float(quantities[index]) if quantities[index] else 0.0
                            ),
                            unit_price=float(units[index]) if units[index] else 0.0,
                            total_price=(
                                float(total_a[index]) if total_a[index] else 0.0
                            ),
                        )
                        items.append(item)

                Products.objects.bulk_create(
                    items
                )  # Use bulk_create to insert multiple items at once
                messages.success(request, "Invoice added successfully.")
        except Exception as e:
            messages.error(request, f"Error occurred while adding invoice: {str(e)}.")
        return render(request, self.template_name, context)
