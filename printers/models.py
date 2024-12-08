from django.db import models

class Printer(models.Model):
    organization = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=True)
    inventory_number = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(protocol='IPv4')
    community = models.CharField(max_length=255, default='public')

    def __str__(self):
        return f"{self.organization} - {self.model} ({self.serial_number})"


class SNMPOID(models.Model):
    CATEGORY_CHOICES = [
        ('id', 'Идентификационные данные'),
        ('metric', 'Метрика'),
    ]

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name='snmp_oids')
    name = models.CharField(max_length=255)  # Название (например, "Серийный номер")
    oid = models.CharField(max_length=255)  # OID для SNMP
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    active = models.BooleanField(default=False)  # Параметр отслеживается

    def __str__(self):
        return f"{self.name} ({self.oid})"


class SNMPHistory(models.Model):
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name='snmp_history')
    oid = models.ForeignKey(SNMPOID, on_delete=models.CASCADE, related_name='history')
    value = models.TextField()  # Сохраненное значение
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.printer} - {self.oid.name} ({self.timestamp})"
