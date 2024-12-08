from django.contrib import admin
from .models import Printer, SNMPOID, SNMPHistory

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ('organization', 'branch', 'model', 'ip_address', 'serial_number', 'inventory_number')
    search_fields = ('organization', 'branch', 'model', 'serial_number', 'ip_address')

@admin.register(SNMPOID)
class SNMPOIDAdmin(admin.ModelAdmin):
    list_display = ('name', 'oid', 'category')
    search_fields = ('name', 'oid', 'category')
    list_filter = ('category',)

@admin.register(SNMPHistory)
class SNMPHistoryAdmin(admin.ModelAdmin):
    list_display = ('printer', 'oid', 'value', 'timestamp')
    search_fields = ('printer__organization', 'printer__model', 'oid__name', 'value')
    list_filter = ('timestamp', 'oid__category')
