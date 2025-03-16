[![Tests](https://github.com/hlebuschek/many-snmp/actions/workflows/tests.yml/badge.svg)](https://github.com/hlebuschek/many-snmp/actions/workflows/tests.yml)
[![Linters](https://github.com/hlebuschek/many-snmp/actions/workflows/lint.yml/badge.svg)](https://github.com/hlebuschek/many-snmp/actions/workflows/lint.yml)
# Установка проекта
* Установить и настроить СУБД
* Установить зависимости backend


# Установка и настройка СУБД 
* Установить postgresql 16 или sqlite3
* Настроить базу данных для проекта (БД, учетная запись)
* В local_setings (файл локальных настроек) - изменить конфигурацию под созданную


# Установка зависиостей
## Через poetry
* Установить poetry - https://python-poetry.org/docs/
* Установить зависимости
```
poetry install
```
## Через pip
```
pip install -r requerments.txt
```
