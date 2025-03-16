from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PrinterViewSet,
    printers_list,
    snmp_poll,
    save_snmp_oid_mapping,
    snmp_history,
    get_snmp_oids,
    save_printer,
    delete_snmp_oid,
    edit_printer,  # Новый маршрут для редактирования принтера
)

# Создаём роутер для REST API
router = DefaultRouter()
router.register(r"printers", PrinterViewSet)

urlpatterns = [
    # API маршруты
    path("api/", include(router.urls)),  # Доступ к API принтеров через маршруты роутера
    # Основной список принтеров
    path(
        "", printers_list, name="printers_list"
    ),  # Отображение всех принтеров на главной странице
    # SNMP маршруты
    path(
        "snmp/poll/<int:printer_id>/", snmp_poll, name="snmp_poll"
    ),  # Выполнение SNMP-опроса
    path(
        "snmp/save_snmp_oid_mapping/<int:printer_id>/",
        save_snmp_oid_mapping,
        name="save_snmp_oid_mapping",
    ),  # Сохранение выбора OID
    path(
        "snmp/history/<int:printer_id>/", snmp_history, name="snmp_history"
    ),  # История опросов SNMP
    path(
        "snmp/oids/<int:printer_id>/", get_snmp_oids, name="get_snmp_oids"
    ),  # Получение списка OID
    # Маршруты для управления принтерами
    path(
        "printers/save/", save_printer, name="save_printer"
    ),  # Сохранение/обновление принтера
    path(
        "printers/<int:printer_id>/edit/", edit_printer, name="edit_printer"
    ),  # Редактирование принтера
    path(
        "snmp/oid/delete/<int:oid_id>/", delete_snmp_oid, name="delete_snmp_oid"
    ),  # Удаление OID
]
