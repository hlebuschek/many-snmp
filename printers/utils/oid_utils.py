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
        # Проверяем, что OID содержит MAC-адрес (например, "mib-2.3.1.1.2.14.1")
        if "mib-2.3.1.1.2.14.1" in oid:
            if isinstance(value, str) and value.startswith("0x"):  # Проверяем, что значение в шестнадцатеричном формате
                try:
                    # Убираем "0x" и преобразуем в стандартный формат MAC-адреса
                    hex_value = value[2:]  # Убираем "0x"
                    if len(hex_value) == 12:  # Проверяем, что длина корректна
                        mac = ":".join([hex_value[i:i+2] for i in range(0, 12, 2)])  # Преобразуем в формат "xx:xx:xx:xx:xx:xx"
                        mac_addresses.append(mac)
                        logger.debug(f"Найден MAC-адрес: {mac} (OID: {oid})")
                    else:
                        logger.warning(f"Некорректная длина MAC-адреса: {value} (OID: {oid})")
                except Exception as e:
                    logger.error(f"Ошибка при обработке MAC-адреса {value}: {e}")
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