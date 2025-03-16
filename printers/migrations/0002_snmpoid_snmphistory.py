# Generated by Django 5.1.4 on 2024-12-07 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("printers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SNMPOID",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("oid", models.CharField(max_length=255)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("id", "Идентификационные данные"),
                            ("metric", "Метрика"),
                        ],
                        max_length=50,
                    ),
                ),
                ("active", models.BooleanField(default=False)),
                (
                    "printer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snmp_oids",
                        to="printers.printer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SNMPHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "printer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snmp_history",
                        to="printers.printer",
                    ),
                ),
                (
                    "oid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="printers.snmpoid",
                    ),
                ),
            ],
        ),
    ]
