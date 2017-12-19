(function ($) {

    'use strict';
    var datatableInit = function () {

        var $table = $('#datatable1');

        $table.dataTable({
            bProcessing: true,
            rowReorder: true,
            sAjaxSource: $table.data('url'),
            "order": [[0, "desc"]],
            "fnReloadAjax": true,
            "fnServerParams": function (data) {
                data.push({"name": 'method', "value": 'list'});
            },
            dom: '<"toolbar"><"search"f>rt<"bottom"ip><"clear">',
            "paginate": true,
            searching: false,
            "columnDefs": [
                {
                    "targets": [1],
                    "visible": false,
                }
            ],
            "initComplete": function (settings, json) {
                this.api().columns().every(function (i) {

                    //if (i == 0){
                    //	return;
                    //}

                    var column = this;
                    var select = $('<select style="width: 100%;"><option value=""></option></select>')
                        .appendTo($(column.footer()).empty()).select2({
                            placeholder: '검색필터',
                            allowClear: true
                        }).attr('width', '100%')
                        .on('change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );

                            column
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });

                    column.data().unique().sort().each(function (d, j) {
                        select.append('<option value="' + d + '">' + d + '</option>')
                    });
                });
            }
        });


        $table.on('click', 'tr', function () {
            var $row;
            var cell;
            var data;
            var t = $('#datatable33').DataTable();
            $row = $(this).closest('tr');
            data = t.row($row.get(0)).data();
            location.href = '/manage/modi_popupZone/' + data[1]
        });
    };


    $(function () {
        datatableInit();
    });

}).apply(this, [jQuery]);


function Search() {
    var table = $('#datatable33').DataTable();
    table.ajax.reload();
}


$.datepicker.setDefaults({
    dateFormat: 'yy-mm-dd',
    prevText: '이전 달',
    nextText: '다음 달',
    monthNames: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    monthNamesShort: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    dayNames: ['일', '월', '화', '수', '목', '금', '토'],
    dayNamesShort: ['일', '월', '화', '수', '목', '금', '토'],
    dayNamesMin: ['일', '월', '화', '수', '목', '금', '토'],
    showMonthAfterYear: true,
    yearSuffix: '년'
});

$(function () {
    $("#datepicker1, #datepicker2").datepicker();
});