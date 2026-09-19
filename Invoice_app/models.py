from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """
    Name: Model representing a customer.
    Description: This model represents a customer in the system.
    Author: stephaneboska@gmail.com
    """

    SEX_TYPES = [("M", "Male"), ("F", "Female")]

    name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    address = models.CharField(max_length=100, null=False, blank=False)
    sex = models.CharField(max_length=1, choices=SEX_TYPES, null=False, blank=False)
    age = models.CharField(max_length=10, null=False, blank=False)
    city = models.CharField(max_length=50, null=False, blank=False)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name


class Invoice(models.Model):
    """
    Name: Model representing an invoice.
    Description: This model represents an invoice associated with a customer.
        It includes fields for the customer, amount, due date, creation timestamp,
        and the user who saved the invoice.
    Author: stephaneboska@gmail.com
    """

    INVOICE_TYPES = [("R", "Receipt"), ("I", "Invoice"), ("P", "Proforma Invoice")]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    save_by = models.ForeignKey(User, on_delete=models.PROTECT)
    invoice_date = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    invoice_type = models.CharField(
        max_length=1, choices=INVOICE_TYPES, null=False, blank=False
    )
    comments = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.customer.name} {self.invoice_date.strftime('%Y-%m-%d')}"

    @property
    def get_total_amount(self):
        total_amount = sum(product.get_total_price for product in self.products_set.all())
        return total_amount

    def get_invoice_type_display(self):
        return dict(self.INVOICE_TYPES).get(self.invoice_type, "Unknown")
        

class Products(models.Model):
    """
    Name: Model representing a product.
    Description: This model represents a product that can be associated with invoices.
    Author: stephaneboska@gmail.com
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="products_set")
    name = models.CharField(max_length=100, null=False, blank=False)
    quantity = models.PositiveIntegerField(null=False, blank=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    @property
    def get_total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.name