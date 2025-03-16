import logging
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
import requests
from .models import Printer, SNMPOID, SNMPHistory
from .serializers import PrinterSerializer
from .utils.oid_utils import load_oid_mapping, extract_mac_addresses, determine_printer_model


logger = logging.getLogger(__name__)

# API ViewSet 
class PrinterViewSet(viewsets.ModelViewSet):
    """
    API для управления принтерами.
    """
    queryset=Printer.objects.all()
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
    Выполняет SNMP-опрос для принтера и обрабатывает данные.
    """
    printer = get_object_or_404(Printer, pk=printer_id)
    node_service_url = "http://localhost:3000/snmp"

    data = [{"ip": printer.ip_address}]
    logger.info(f"Инициирование SNMP-опроса для принтера ID {printer_id}, IP: {printer.ip_address}")

    try:
        response = requests.post(node_service_url, json=data, timeout=120)
        response.raise_for_status()

        response_data = response.json()
        logger.info(f"SNMP-опрос успешен. Получены данные: {response_data}")

        if not isinstance(response_data, list):
            logger.error(f"Неожиданный формат ответа: {response_data}")
            return JsonResponse({"error": "Unexpected response format"}, status=500)

        # Загружаем справочник OID
        oid_to_model = load_oid_mapping("./printers/utils/sysobject.ids")

        # Обрабатываем данные
        for result in response_data:
            logger.info(f"Обработка данных для принтера {printer_id}")

            # Извлекаем MAC-адреса
            mac_addresses = extract_mac_addresses(result)
            logger.info(f"Извлечено MAC-адресов: {mac_addresses}")
            printer.mac_addresses = ", ".join(mac_addresses)  # Сохраняем MAC-адреса в модель

            # Определяем модель принтера
            printer.model = determine_printer_model(result, oid_to_model)
            logger.info(f"Определена модель принтера: {printer.model}")

            # Сохраняем изменения
            printer.save()
            logger.info(f"Данные принтера {printer_id} успешно обновлены.")

        return JsonResponse(response_data, safe=False)

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Ошибка при выполнении SNMP-опроса для принтера ID {printer_id}: {req_err}")
        return JsonResponse({"error": "Error during SNMP request"}, status=500)
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке данных для принтера {printer_id}: {e}")
        return JsonResponse({"error": "Unexpected error"}, status=500)


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
