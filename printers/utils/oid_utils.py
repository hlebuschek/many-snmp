import logging

logger = logging.getLogger(__name__)

def load_oid_mapping(file_path):
    """
    Загружает справочник OID из файла и возвращает словарь {oid: model}.
    """
    oid_to_model = {}
    logger.info(f"Загрузка справочника OID из файла: {file_path}")

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    parts = line.strip().split('\t')  # Разделяем строку по табуляции
                    if len(parts) >= 4:  # Проверяем, что строка содержит OID, производителя, тип и модель
                        oid = parts[0]
                        model = parts[3]  # Модель устройства
                        oid_to_model[oid] = model
                        logger.debug(f"Добавлен OID: {oid} -> Модель: {model}")
                    else:
                        logger.warning(f"Некорректная строка в файле: {line.strip()}")
        logger.info(f"Справочник OID успешно загружен. Загружено {len(oid_to_model)} записей.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке справочника OID: {e}")
        raise

    return oid_to_model


def extract_mac_addresses(snmp_data):
    """
    Извлекает MAC-адреса из данных SNMP.
    """
    mac_addresses = []
    logger.info("Начало извлечения MAC-адресов из данных SNMP.")

    for oid, value in snmp_data.items():
        if oid.startswith("1.3.6.1.2.1.2.2.1.6"):  # OID для MAC-адреса
            if isinstance(value, str) and len(value) == 12:  # Проверяем, что это MAC-адрес
                mac_addresses.append(value)
                logger.debug(f"Найден MAC-адрес: {value} (OID: {oid})")
            else:
                logger.warning(f"Некорректное значение MAC-адреса: {value} (OID: {oid})")
        else:
            logger.debug(f"Пропущен OID: {oid} (не относится к MAC-адресам)")

    logger.info(f"Извлечено {len(mac_addresses)} MAC-адресов.")
    return mac_addresses

def determine_printer_model(snmp_data, oid_to_model):
    """
    Определяет модель принтера на основе OID из справочника.
    """
    logger.info("Начало определения модели принтера.")

    for oid, value in snmp_data.items():
        if oid in oid_to_model:
            model = oid_to_model[oid]
            logger.info(f"Определена модель принтера: {model} (OID: {oid})")
            return model
        else:
            logger.debug(f"OID {oid} не найден в справочнике.")

    logger.warning("Модель принтера не определена.")
    return "Unknown"