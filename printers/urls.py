from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PrinterViewSet,
    printers_list,
    snmp_poll,
    save_oid_mapping,
    snmp_history,
    get_snmp_oids,
    save_printer,
)

router = DefaultRouter()
router.register(r'printers', PrinterViewSet)

urlpatterns = [
    # API маршруты
    path('api/', include(router.urls)),

    # Основной список принтеров
    path('', printers_list, name='printers_list'),

    # SNMP маршруты
    path('snmp/poll/<int:printer_id>/', snmp_poll, name='snmp_poll'),
    path('snmp/save_oid_mapping/<int:printer_id>/', save_oid_mapping, name='save_oid_mapping'),
    path('snmp/history/<int:printer_id>/', snmp_history, name='snmp_history'),
    path('snmp/oids/<int:printer_id>/', get_snmp_oids, name='get_snmp_oids'),

    # Маршрут для сохранения принтера
    path('printers/save/', save_printer, name='save_printer'),
]
