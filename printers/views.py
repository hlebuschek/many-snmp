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
    node_service_url = "http://localhost:3000/snmp"

    data = [{"ip": printer.ip_address}]
    logger.info(f"Initiating SNMP poll for printer ID {printer_id}, IP: {printer.ip_address}")

    try:
        response = requests.post(node_service_url, json=data, timeout=120)
        response.raise_for_status()

        response_data = response.json()
        logger.info(f"SNMP poll successful. Data received: {response_data}")

        if not isinstance(response_data, list):
            logger.error(f"Unexpected response format: {response_data}")
            return JsonResponse({"error": "Unexpected response format"}, status=500)

        existing_oids = SNMPOID.objects.filter(printer=printer).values("oid", "name", "active", "category")
        for result in response_data:
            result_oid = result.get('oid')
            match = next((oid for oid in existing_oids if oid['oid'] == result_oid), None)
            if match:
                result['active'] = match['active']
                result['name'] = match['name']
                result['category'] = match['category']
            else:
                result['active'] = False
                result['category'] = "metric"

        return JsonResponse(response_data, safe=False)

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Error during SNMP poll for printer ID {printer_id}: {req_err}")
        return JsonResponse({"error": "Error during SNMP request"}, status=500)


def get_snmp_oids(request, printer_id):
    """
    Возвращает список OID для указанного принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    oids = printer.snmp_oids.values("id", "name", "oid", "category", "active")
    logger.info(f"Retrieved OIDs for printer ID {printer_id}: {list(oids)}")
    return JsonResponse(list(oids), safe=False)


def save_snmp_oid_mapping(request, printer_id):
    """
    Сохраняет или обновляет настройки OID для указанного принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for oid_data in data.get('oids', []):
                oid = oid_data.get('oid')
                category = oid_data.get('category')
                active = oid_data.get('active', True)

                if not oid or not category:
                    continue

                SNMPOID.objects.update_or_create(
                    printer=printer,
                    oid=oid,
                    defaults={'category': category, 'active': active, 'user_defined': True}
                )

            return JsonResponse({'message': 'Настройки OID успешно сохранены'})
        except Exception as e:
            logger.error(f"Error saving OID mapping for printer {printer_id}: {e}")
            return JsonResponse({'error': f'Ошибка сохранения: {str(e)}'}, status=400)
    return JsonResponse({'error': 'Неверный метод'}, status=405)


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
    logger.info(f"Retrieved SNMP history for printer {printer_id}: {data}")
    return JsonResponse({'history': data})


def save_printer(request):
    """
    Сохраняет новый принтер или обновляет существующий.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            printer_id = data.get('id')
            if printer_id:
                printer = get_object_or_404(Printer, pk=printer_id)
                for field, value in data.items():
                    setattr(printer, field, value)
                printer.save()
                logger.info(f"Printer ID {printer_id} updated")
            else:
                printer = Printer.objects.create(**data)
                logger.info(f"New printer created: {printer}")
            return JsonResponse({'message': 'Принтер успешно сохранён'})
        except Exception as e:
            logger.error(f"Error saving printer: {e}")
            return JsonResponse({'error': 'Ошибка сохранения принтера'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


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


def edit_printer(request, printer_id):
    """
    Возвращает данные принтера для редактирования.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'GET':
        return JsonResponse({
            'id': printer.id,
            'organization': printer.organization,
            'branch': printer.branch,
            'city': printer.city,
            'address': printer.address,
            'model': printer.model,
            'serial_number': printer.serial_number,
            'inventory_number': printer.inventory_number,
            'ip_address': printer.ip_address,
        })
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


def update_printer(request, printer_id):
    """
    Обновляет данные принтера.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(printer, field, value)
            printer.save()
            logger.info(f"Printer ID {printer_id} updated successfully")
            return JsonResponse({'message': 'Принтер успешно обновлён'})
        except Exception as e:
            logger.error(f"Error updating printer {printer_id}: {e}")
            return JsonResponse({'error': f'Ошибка обновления: {str(e)}'}, status=400)
    return JsonResponse({'error': 'Неверный метод'}, status=405)
