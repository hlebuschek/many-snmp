$(document).ready(function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Fetch printers and populate the table
    function fetchPrinters() {
        $.ajax({
            url: '/api/printers/',
            method: 'GET',
            success: function (data) {
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
            error: function () {
                toastr.error('Ошибка загрузки данных принтеров');
            }
        });
    }

    // SNMP Poll button handler
    $(document).on('click', '.snmp-btn', function () {
        const printerId = $(this).data('id');
        $('#snmpTableBody').empty();
        $.ajax({
            url: `/snmp/poll/${printerId}/`,
            method: 'GET',
            success: function (response) {
                const oids = response.oids || [];
                oids.forEach((oid) => {
                    $('#snmpTableBody').append(`
                        <tr>
                            <td>${oid.name || 'Не указано'}</td>
                            <td>${oid.oid || 'N/A'}</td>
                            <td>${oid.type || 'N/A'}</td>
                            <td>${oid.value || 'N/A'}</td>
                            <td>
                                <input type="checkbox" class="form-check-input" data-oid-id="${oid.id}" ${oid.active ? 'checked' : ''}>
                            </td>
                        </tr>
                    `);
                });
                $('#snmpResultModal').modal('show');
            },
            error: function (xhr, status, error) {
                toastr.error('Ошибка выполнения SNMP-опроса');
                console.error("Ошибка SNMP-опроса:", xhr.responseText || error);
            }
        });
    });

    // Save selected OIDs
    $('#snmpForm').submit(function (e) {
        e.preventDefault();
        const printerId = $('#snmpTableBody').data('printer-id'); // Add printer ID to the form
        const selectedOids = [];
        $('#snmpTableBody input:checked').each(function () {
            selectedOids.push($(this).data('oid-id'));
        });

        $.ajax({
            url: `/snmp/save_oid_mapping/${printerId}/`,
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            contentType: 'application/json',
            data: JSON.stringify({ oids: selectedOids }),
            success: function () {
                toastr.success('Выбор OID сохранён');
                $('#snmpResultModal').modal('hide');
            },
            error: function () {
                toastr.error('Ошибка сохранения выбора OID');
            }
        });
    });

    // Edit printer
    $(document).on('click', '.edit-btn', function () {
        const printerId = $(this).data('id');
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

    // Delete printer
    $(document).on('click', '.delete-btn', function () {
        const printerId = $(this).data('id');
        if (confirm('Вы уверены, что хотите удалить этот принтер?')) {
            $.ajax({
                url: `/api/printers/${printerId}/`,
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken },
                success: function () {
                    toastr.success('Принтер удалён');
                    fetchPrinters();
                },
                error: function () {
                    toastr.error('Ошибка удаления принтера');
                }
            });
        }
    });

    // Add/Edit printer form submit
    $('#printerForm').submit(function (e) {
        e.preventDefault();
        const id = $('#printerId').val();
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/printers/${id}/` : '/api/printers/';
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
            url: url,
            method: method,
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

    // Initial fetch
    fetchPrinters();
});
