import logging
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
import requests
from .models import Printer, SNMPOID, SNMPHistory
from .serializers import PrinterSerializer

logger = logging.getLogger(__name__)

# API ViewSet
class PrinterViewSet(viewsets.ModelViewSet):
    """
    API для управления принтерами.
    """
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer


# Веб-функции
def printers_list(request):
    """
    Отображение списка принтеров.
    """
    printers = Printer.objects.all()
    logger.info(f"Render printers list. Count: {printers.count()}")
    return render(request, 'printers/list.html', {'printers': printers})


# SNMP опрос через Node.js сервис
def snmp_poll(request, printer_id):
    """
    Выполняет SNMP запрос для принтера через Node.js сервис.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    node_service_url = "http://localhost:3000/snmp"  # URL вашего Node.js сервиса

    data = {
        "ip": printer.ip_address,
        "community": printer.community or "public"
    }

    logger.info(f"Initiating SNMP poll for printer ID {printer_id}, IP: {printer.ip_address}")

    try:
        response = requests.post(node_service_url, json=data, timeout=10)
        response.raise_for_status()

        logger.info(f"SNMP poll successful for printer ID {printer_id}")
        # Combine SNMP response with existing OIDs
        existing_oids = SNMPOID.objects.filter(printer=printer).values("oid", "name", "active")
        response_data = response.json()
        for result in response_data:
            match = next((oid for oid in existing_oids if oid['oid'] == result['oid']), None)
            if match:
                result['active'] = match['active']
                result['name'] = match['name']
            else:
                result['active'] = False
        return JsonResponse(response_data, safe=False)
    except requests.RequestException as e:
        logger.error(f"SNMP poll failed for printer ID {printer_id}: {e}")
        return JsonResponse({"error": "Ошибка взаимодействия с SNMP-сервисом"}, status=500)


# Получение списка OID для принтера
def get_snmp_oids(request, printer_id):
    """
    Возвращает список OID для указанного принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    oids = printer.snmp_oids.values("id", "name", "oid", "category", "active")
    logger.info(f"Retrieved OIDs for printer ID {printer_id}: {list(oids)}")
    return JsonResponse(list(oids), safe=False)


# Сохранение маппинга OID
def save_oid_mapping(request, printer_id):
    """
    Сохраняет пользовательский маппинг OID для указанного принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        logger.info(f"Saving OID mapping for printer: {printer}")
        try:
            data = json.loads(request.body)
            active_oids = data.get('active_oids', [])
            SNMPOID.objects.filter(printer=printer).update(active=False)
            SNMPOID.objects.filter(id__in=active_oids).update(active=True)
            logger.info(f"Active OIDs updated for printer ID {printer_id}")
            return JsonResponse({'message': 'OID выбор успешно сохранён'})
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON data for printer {printer_id}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    logger.error(f"Invalid method used for saving OID mapping for printer {printer_id}")
    return JsonResponse({'error': 'Invalid method'}, status=405)


# История SNMP опросов
def snmp_history(request, printer_id):
    """
    Возвращает историю значений SNMP для указанного принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    history = SNMPHistory.objects.filter(printer=printer).select_related('oid').order_by('-timestamp')
    data = [
        {
            'oid': entry.oid.oid,
            'name': entry.oid.name,
            'value': entry.value,
            'timestamp': entry.timestamp,
        }
        for entry in history
    ]
    logger.info(f"Retrieved SNMP history for printer {printer}: {data}")
    return JsonResponse({'history': data})


# Сохранение нового принтера
def save_printer(request):
    """
    Сохраняет новый принтер или обновляет существующий.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            printer_id = data.get('id')
            if printer_id:
                # Обновляем принтер
                printer = get_object_or_404(Printer, pk=printer_id)
                for field, value in data.items():
                    setattr(printer, field, value)
                printer.save()
                logger.info(f"Printer ID {printer_id} updated")
            else:
                # Создаем новый принтер
                printer = Printer.objects.create(**data)
                logger.info(f"New printer created: {printer}")
            return JsonResponse({'message': 'Принтер успешно сохранён'})
        except Exception as e:
            logger.error(f"Error saving printer: {e}")
            return JsonResponse({'error': 'Ошибка сохранения принтера'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


# Удаление OID (если потребуется)
def delete_snmp_oid(request, oid_id):
    """
    Удаляет OID из базы данных.
    """
    try:
        oid = get_object_or_404(SNMPOID, pk=oid_id)
        oid.delete()
        logger.info(f"OID {oid_id} deleted successfully.")
        return JsonResponse({'message': 'OID успешно удалён'})
    except Exception as e:
        logger.error(f"Error deleting OID {oid_id}: {e}")
        return JsonResponse({'error': 'Ошибка удаления OID'}, status=400)
