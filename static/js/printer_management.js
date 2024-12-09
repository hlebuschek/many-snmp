$(document).ready(function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Функция для загрузки списка принтеров
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
                console.error("Ошибка загрузки данных принтеров:", xhr.responseText);
                toastr.error('Ошибка загрузки данных принтеров');
            }
        });
    }

    // Обработчик для кнопки "Редактировать"
    $(document).on('click', '.edit-btn', function () {
        const printerId = $(this).data('id');
        console.log(`Редактируем принтер с ID: ${printerId}`);

        $.ajax({
            url: `/printers/${printerId}/edit/`,
            method: 'GET',
            success: function (data) {
                console.log("Получены данные принтера для редактирования:", data);

                // Заполняем данные в форму модального окна
                $('#addPrinterModal input[name="id"]').val(data.id);
                $('#addPrinterModal input[name="organization"]').val(data.organization);
                $('#addPrinterModal input[name="branch"]').val(data.branch);
                $('#addPrinterModal input[name="city"]').val(data.city);
                $('#addPrinterModal input[name="address"]').val(data.address);
                $('#addPrinterModal input[name="model"]').val(data.model);
                $('#addPrinterModal input[name="serial_number"]').val(data.serial_number);
                $('#addPrinterModal input[name="inventory_number"]').val(data.inventory_number);
                $('#addPrinterModal input[name="ip_address"]').val(data.ip_address);

                // Показываем модальное окно редактирования
                $('#addPrinterModal').modal('show');
            },
            error: function (xhr) {
                console.error("Ошибка получения данных принтера для редактирования:", xhr.responseText);
                toastr.error('Ошибка загрузки данных для редактирования');
            }
        });
    });

    // Сохранение изменений принтера
    $('#editPrinterForm').submit(function (e) {
        e.preventDefault();

        const printerId = $('#addPrinterModal input[name="id"]').val();
        console.log(`Сохраняем изменения для принтера с ID: ${printerId}`);

        const formData = {
            organization: $('#addPrinterModal input[name="organization"]').val(),
            branch: $('#addPrinterModal input[name="branch"]').val(),
            city: $('#addPrinterModal input[name="city"]').val(),
            address: $('#addPrinterModal input[name="address"]').val(),
            model: $('#addPrinterModal input[name="model"]').val(),
            serial_number: $('#addPrinterModal input[name="serial_number"]').val(),
            inventory_number: $('#addPrinterModal input[name="inventory_number"]').val(),
            ip_address: $('#addPrinterModal input[name="ip_address"]').val(),
        };

        console.log("Данные для отправки:", formData);

        $.ajax({
            url: `/printers/${printerId}/update/`,
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function () {
                toastr.success('Данные принтера обновлены');
                console.log("Данные принтера успешно обновлены.");
                $('#addPrinterModal').modal('hide');
                fetchPrinters(); // Обновляем список принтеров
            },
            error: function (xhr) {
                console.error("Ошибка сохранения изменений принтера:", xhr.responseText);
                toastr.error('Ошибка сохранения изменений');
            }
        });
    });

    // Первоначальная загрузка списка принтеров
    console.log("Загрузка списка принтеров...");
    fetchPrinters();
});
