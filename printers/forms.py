from django import forms

from .models import Printer


class PrinterForm(forms.ModelForm):
    class Meta:
        model = Printer
        fields = [
            "organization",
            "branch",
            "city",
            "address",
            "model",
            "serial_number",
            "inventory_number",
            "ip_address",
        ]
