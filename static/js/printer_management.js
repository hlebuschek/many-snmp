$(document).ready(function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Функция для загрузки списка принтеров fff
    function fetchPrinters() {
        console.log("Начало загрузки списка принтеров...");
        $.ajax({
            url: '/api/printers/',
            method: 'GET',
            success: function (data) {
                console.log("Получен список принтеров:", data);
                $('#printerTableBody').empty();
                data.forEach(function (printer) {
                    $('#printerTableBody').append(
                        `<tr>
                            <td>${printer.id}</td>
                            <td>${printer.organization}</td>
                            <td>${printer.branch}</td>
                            <td>${printer.city}</td>
                            <td>${printer.address}</td>
                            <td>${printer.model}</td>
                            <td>${printer.serial_number}</td>
                            <td>${printer.inventory_number}</td>
                            <td>${printer.ip_address}</td>
                            <td>
                                <button class="btn btn-secondary snmp-btn" data-id="${printer.id}">SNMP Опрос</button>
                                <button class="btn btn-info edit-btn" data-id="${printer.id}">Редактировать</button>
                                <button class="btn btn-danger delete-btn" data-id="${printer.id}">Удалить</button>
                            </td>
                        </tr>`
                    );
                });
            },
            error: function (xhr) {
                toastr.error('Ошибка загрузки данных принтеров');
                console.error("Ошибка загрузки данных принтеров:", xhr.responseText);
            }
        });
    }

    // SNMP Poll: запрос данных SNMP для выбранного принтера
    $(document).on('click', '.snmp-btn', function () {
        const printerId = $(this).data('id');
        console.log(`Выполняем SNMP-опрос для принтера с ID: ${printerId}`);
        $('#snmpResultModal').data('printer-id', printerId);
        const button = $(this);
        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Опрос...');

        $('#snmpTableBody').empty();

        $.ajax({
            url: `/snmp/poll/${printerId}/`,
            method: 'GET',
            success: function (response) {
                console.log("Ответ SNMP:", response);
                button.prop('disabled', false).html('SNMP Опрос');

                const parsedResponse = Object.entries(response[0]);
                parsedResponse.forEach(([oid, value]) => {
                    const displayValue = typeof value === 'object' ? JSON.stringify(value) : value;
                    $('#snmpTableBody').append(`
                        <tr>
                            <td>${oid}</td>
                            <td>${displayValue}</td>
                            <td>
                                <select class="form-select" data-oid-id="${oid}">
                                    <option value="">Не записывать</option>
                                    <option value="mac_address">MAC-адрес</option>
                                    <option value="serial_number">Серийный номер</option>
                                    <option value="a4_bw">A4 Ч/Б</option>
                                    <option value="a3_bw">A3 Ч/Б</option>
                                    <option value="a4_color">A4 Цветная</option>
                                    <option value="a3_color">A3 Цветная</option>
                                </select>
                            </td>
                        </tr>
                    `);
                });

                $('#snmpResultModal').modal('show');
            },
            error: function (xhr) {
                button.prop('disabled', false).html('SNMP Опрос');
                toastr.error('Ошибка выполнения SNMP-опроса');
                console.error("Ошибка выполнения SNMP-опроса:", xhr.responseText);
            }
        });
    });

    // Сохранение выбора OID после SNMP-опроса
    $('#snmpForm').submit(function (e) {
        e.preventDefault();
        const printerId = $('#snmpResultModal').data('printer-id');
        const selectedOids = [];
        $('#snmpTableBody tr').each(function () {
            const oidId = $(this).find('select').data('oid-id');
            const category = $(this).find('select').val();
            if (category) selectedOids.push({ oid: oidId, category });
        });

        $.ajax({
            url: `/snmp/save_snmp_oid_mapping/${printerId}/`,
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            contentType: 'application/json',
            data: JSON.stringify({ oids: selectedOids }),
            success: function () {
                toastr.success('OID шаблон сохранён');
                $('#snmpResultModal').modal('hide');
            },
            error: function (xhr) {
                toastr.error('Ошибка сохранения OID шаблона');
                console.error("Ошибка сохранения OID шаблона:", xhr.responseText);
            }
        });
    });

    // Редактирование принтера
    $(document).on('click', '.edit-btn', function () {
        const printerId = $(this).data('id');
        console.log(`Открытие формы редактирования для принтера с ID: ${printerId}`);
        $.ajax({
            url: `/api/printers/${printerId}/`,
            method: 'GET',
            success: function (printer) {
                $('#printerId').val(printer.id);
                $('#organization').val(printer.organization);
                $('#branch').val(printer.branch);
                $('#city').val(printer.city);
                $('#address').val(printer.address);
                $('#model').val(printer.model);
                $('#serial_number').val(printer.serial_number);
                $('#inventory_number').val(printer.inventory_number);
                $('#ip_address').val(printer.ip_address);

                $('#addPrinterModalLabel').text('Редактировать принтер');
                $('#addPrinterModal').modal('show');
            },
            error: function () {
                toastr.error('Ошибка загрузки данных принтера');
            }
        });
    });

    // Очистка формы перед добавлением нового принтера
    $(document).on('click', '.add-btn', function () {
        console.log("Очистка формы и открытие модального окна для нового принтера");
        $('#printerForm')[0].reset(); // Сбрасываем значения формы
        $('#printerId').val(''); // Очищаем ID для нового принтера
        $('#addPrinterModalLabel').text('Добавить новый принтер');
        $('#addPrinterModal').modal('show');
    });

    // Сохранение нового или обновлённого принтера
    $('#printerForm').submit(function (e) {
        e.preventDefault();
        const id = $('#printerId').val();
        const url = id ? `/api/printers/${id}/` : '/api/printers/';
        const method = id ? 'PUT' : 'POST';
        const formData = {
            organization: $('#organization').val(),
            branch: $('#branch').val(),
            city: $('#city').val(),
            address: $('#address').val(),
            model: $('#model').val(),
            serial_number: $('#serial_number').val(),
            inventory_number: $('#inventory_number').val(),
            ip_address: $('#ip_address').val()
        };

        $.ajax({
            url,
            method,
            headers: { 'X-CSRFToken': csrftoken },
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function () {
                toastr.success(id ? 'Принтер обновлён' : 'Принтер добавлен');
                $('#addPrinterModal').modal('hide');
                fetchPrinters();
            },
            error: function () {
                toastr.error('Ошибка сохранения принтера');
            }
        });
    });

    // Удаление принтера
    $(document).on('click', '.delete-btn', function () {
        const printerId = $(this).data('id');
        console.log(`Удаляем принтер с ID: ${printerId}`);
        if (confirm('Вы уверены, что хотите удалить этот принтер?')) {
            $.ajax({
                url: `/api/printers/${printerId}/`,
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken },
                success: function () {
                    toastr.success('Принтер успешно удалён');
                    fetchPrinters(); // Обновляем список принтеров
                },
                error: function (xhr) {
                    toastr.error('Ошибка удаления принтера');
                    console.error("Ошибка удаления принтера:", xhr.responseText);
                }
            });
        }
    });

    // Первоначальная загрузка
    fetchPrinters();
});
