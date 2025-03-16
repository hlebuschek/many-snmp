from rest_framework import serializers

from .models import SNMPOID, Printer


class SNMPOIDSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели SNMPOID.
    Включает категории, активность и полное описание OID.
    """

    class Meta:
        model = SNMPOID
        fields = "__all__"  # Включает все поля модели SNMPOID


class PrinterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Printer.
    Добавлено поле snmp_oids для отображения связанных OID.
    """

    snmp_oids = SNMPOIDSerializer(
        many=True, read_only=True
    )  # Отображаем связанные OID в принтере

    class Meta:
        model = Printer
        fields = "__all__"  # Включает все поля модели Printer и связанные OID
