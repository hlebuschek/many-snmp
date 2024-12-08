$(document).ready(function () {
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
                            <td>
                                <button class="btn btn-danger delete-btn" data-id="${printer.id}">Удалить</button>
                            </td>
                        </tr>`
                    );
                });

                $('.delete-btn').click(function () {
                    const printerId = $(this).data('id');
                    deletePrinter(printerId);
                });
            },
            error: function () {
                toastr.error('Ошибка при загрузке данных');
            }
        });
    }

    $('#submitPrinterForm').click(function () {
        const formData = new FormData($('#addPrinterForm')[0]);
        $.ajax({
            url: '/api/printers/',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                toastr.success('Принтер успешно добавлен!');
                $('#addPrinterModal').modal('hide');
                fetchPrinters();
            },
            error: function () {
                toastr.error('Ошибка при добавлении принтера');
            }
        });
    });

    fetchPrinters();
});
