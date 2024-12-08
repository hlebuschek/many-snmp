from rest_framework import serializers
from .models import Printer, SNMPOID

class SNMPOIDSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели SNMPOID
    """
    class Meta:
        model = SNMPOID
        fields = '__all__'  # Включает все поля модели


class PrinterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Printer.
    Добавлено поле snmp_oids для отображения связанных OID.
    """
    snmp_oids = SNMPOIDSerializer(many=True, read_only=True)  # Отображаем связанные OID в принтере

    class Meta:
        model = Printer
        fields = '__all__'  # Включает все поля модели Printer + snmp_oids
