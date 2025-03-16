from django.db import models


class Printer(models.Model):
    organization = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)  # Модель принтера
    serial_number = models.CharField(max_length=255, unique=True)
    inventory_number = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(protocol="IPv4")
    community = models.CharField(max_length=255, default="public")
    mac_addresses = models.TextField(blank=True, null=True)  # MAC-адреса

    def __str__(self):
        return f"{self.organization} - {self.model} ({self.serial_number})"


class SNMPOID(models.Model):
    CATEGORY_CHOICES = [
        ("mac_address", "MAC-адрес"),
        ("serial_number", "Серийный номер"),
        ("a4_bw", "A4 Ч/Б"),
        ("a3_bw", "A3 Ч/Б"),
        ("a4_color", "A4 Цветная"),
        ("a3_color", "A3 Цветная"),
        ("id", "Идентификационные данные"),
        ("metric", "Метрика"),
    ]

    printer = models.ForeignKey(
        Printer, on_delete=models.CASCADE, related_name="snmp_oids"
    )
    name = models.CharField(max_length=255)  # Название (например, "Серийный номер")
    oid = models.CharField(max_length=255)  # OID для SNMP
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
    )  # Категория, выбранная пользователем
    active = models.BooleanField(default=False)  # Используется ли этот OID
    user_defined = models.BooleanField(
        default=False
    )  # Является ли настройка пользовательской

    def __str__(self):
        return f"{self.printer} - {self.name} ({self.oid}) [{self.category}]"


class SNMPHistory(models.Model):
    printer = models.ForeignKey(
        Printer, on_delete=models.CASCADE, related_name="snmp_history"
    )
    oid = models.ForeignKey(SNMPOID, on_delete=models.CASCADE, related_name="history")
    value = models.TextField()  # Сохраненное значение
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.printer} - {self.oid.name} ({self.timestamp})"
