from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from .models import *
from django.contrib import messages
from django.db import transaction
from .utils import pagination, get_invoice
from django.template.loader import get_template  # to retrieve an html file
from django.contrib.auth.decorators import login_required # used for functions
from django.contrib.auth.mixins import LoginRequiredMixin # used for classes
from django.utils.translation import gettext as _


import datetime
import os
import pdfkit

from .decorator import *


# Create your views here.
class HomeView(LoginRequiredSuperuserMixin, View):
    """
    Home view for the invoice application.
    Renders the index.html template.
    """

    template_name = "index.html"
    """
    select_related is used to optimize database queries by fetching related objects in a single query, reducing the number of database hits.
    In this case, it fetches the related 'customer' object for each invoice, which can improve performance when displaying invoice data along with customer information.
    """
    invoices = (
        Invoice.objects.select_related("customer", "save_by")
        .all()
        .order_by("-invoice_date")
    )  # display the recent invoices saved
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
                messages.success(request, _("Changes made successfully."))
            except Exception as e:
                messages.error(request, _(f"Sorry, an error has occured: {e}"))

        # deleting
        if request.POST.get("id_supprimer"):
            try:
                obj = Invoice.objects.get(pk=request.POST.get("id_supprimer"))
                obj.delete()
                messages.success(request, _("Deletion was successful."))
            except Exception as e:
                messages.error(request, _(f"Sorry, an error has occured: {e}"))

        # placed here to update the displayed data
        items = pagination(request, self.invoices)  # Paginate the invoices
        self.context["invoices"] = items  # Update the context with paginated invoices
        return render(request, self.template_name, self.context)


class AddCustomerView(LoginRequiredSuperuserMixin, View):
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
                messages.success(request, _("Customer added successfully."))
            else:
                messages.error(request, _("Error, try again."))
        except Exception as e:
            messages.error(request, _(f"Error occurred while adding customer: {str(e)}"))

        return render(request, self.template_name)


class AddInvoiceView(LoginRequiredSuperuserMixin, View):
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
                    messages.error(request, _("Please add at least one article."))
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
                messages.success(request, _("Invoice added successfully."))
        except Exception as e:
            messages.error(request, _(f"Error occurred while adding invoice: {str(e)}."))
        return render(request, self.template_name, context)


class InvoiceVisualisationView(LoginRequiredSuperuserMixin, View):
    """
    View for visualising an Invoice.
    Renders the invoice.html template.
    """

    # the variables in context should be the same names like that one used in the template
    template_name = "invoice.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        context = get_invoice(pk)

        return render(request, self.template_name, context)

@superuser_required
def get_invoice_pdf(request, *args, **kwargs):
    """
    generate pdf file from html file

    """

    # Dynamically build the path using the ProgramFiles environment variable
    program_files = os.environ.get('ProgramFiles', r'C:\Program Files')
    path_wkhtmltopdf = os.path.join(program_files, 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')

    # Pass the path to the pdfkit configuration
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pk = kwargs.get('pk')
    context = get_invoice(pk)
    context["date"] = datetime.datetime.today()
    context["base_url"] = request.build_absolute_uri('/')

    # get html file
    template = get_template("invoice_pdf.html")

    # render html file with context
    html = template.render(context, request)

    # pdf format options
    options = {
        'page-size':'Letter',
        'encoding': 'UTF-8',
        # 'enable-local-file-access': '',
        'load-error-handling': 'ignore',       
        'load-media-error-handling': 'ignore'
    }

    # generate the pdf file
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachement; filename="invoice_{pk}.pdf"'

    return response