jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    setDataTable1();
    setDataTable2();

    $.ajax({
        url: '/manage/multisite_org/',
        data: {
            method: 'org'
        }
    }).done(function (data) {
        var html = "<option value='None'>선택하세요.</option>";
        for (var i = 0; i < data.length; i++) {
            //alert(data[key]);
            html += "<option value=" + data[i][0] + ">" + data[i][1] + "</option>"
        }
        $('#org').html(html);
    });

});

function setDataTable1() {
    var $table = $('#datatable1');

    $table.dataTable({
        dom: '<"toolbar"><"search">rt<"bottom"ip><"clear">',
        scrollX: true,
        bProcessing: true,
        ordering: false,
        serverSide: false,
        searching: true,
        "language": {
            "emptyTable": "조회된 데이터가 없습니다."
        },
        "scrollY": "400px",
        "scrollCollapse": true,
        ajax: {
            url: "/manage/series_course_list",
            type: "GET",
            dataType: "json",
            data: buildSearchData1,
            dataSrc: function (json) {
                return json.data;
            }
        },
        columns: [
            {data: "pk", name: "pk"},
            {data: "rn"},
            {data: "org"},
            {data: "display_number_with_default"},
            {data: "course_name"},
        ],
        columnDefs: [
            {
                targets: 0, visible: true, name: "pk", render: function (data) {
                return '<input type="checkbox" name="' + data + '" value="' + data + '">';
            },
            },
            {
                targets: 4, visible: true, render: function (data, type) {
                return '<p style="display:none">' + data + '</p><input type="text" class = "form-control" name="' + data + '" value="' + data + '">';
            },
            },
        ],
        rowsGroup: [
            0,
            5
        ],
        paginate: false,
        "info": false,
        initComplete: fnInitComplete
    })
    ;
}

var fnInitComplete = function () {
    $('.form-control').change(function () {
        $(this).parent().parent().find('input:checkbox').prop("checked", true);
    });
}

function setDataTable2() {
    var $table = $('#datatable2');

    $table.dataTable({
        dom: '<"toolbar"><"search">rt<"bottom"ip><"clear">',
        scrollX: true,
        bProcessing: true,
        ordering: false,
        serverSide: false,
        searching: true,
        "language": {
            "emptyTable": "조회된 데이터가 없습니다."
        },
        "scrollY": "400px",
        "scrollCollapse": true,
        ajax: {
            url: "/manage/all_course",
            type: "GET",
            dataType: "json",
            data: buildSearchData2,
            dataSrc: function (json) {
                return json.data;
            }
        },
        columns: [
            {data: "pk", name: "pk"},
            {data: "id"},
            {data: "rn"},
            {data: "detail_name"},
            {data: "display_name"},
            {data: "course"},

        ],
        columnDefs: [
            {
                targets: 0, visible: true, name: "pk", render: function (data, type) {
                return '<input type="checkbox" name="' + data + '" value="' + data + '">';
            },
            },
            {targets: 1, visible: false},

        ],
        rowsGroup: [
            0,
            5
        ],
        paginate: false,
        "info": false,
        initComplete: function () {
        }
    })
    ;
    $('#search_input').on('keyup', function () {
        $table.api()
            .search(this.value)
            .draw();
    });

}


function buildSearchData1() {
    var obj = {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        series_id: '{{id}}',
        method: 'list',
    }
    return obj
}


function buildSearchData2() {

    var org = $('#org').val();
    var obj = {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        user_id: '{{ user_id }}',
        series_id: '{{id}}',
        org: org,
    }
    return obj
}

function checked_all1() {
    console.log($("#check_all1").is(":checked"));

    if ($("#check_all1").is(":checked")) {
        $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", true);
    } else {
        $("#datatable1 tbody input[type=checkbox]:visible").prop("checked", false);
    }
}

function checked_all2() {
    console.log($("#check_all2").is(":checked"));

    if ($("#check_all2").is(":checked")) {
        $("#datatable2 tbody input[type=checkbox]:visible").prop("checked", true);
    } else {
        $("#datatable2 tbody input[type=checkbox]:visible").prop("checked", false);
    }
}

function update1() {
    var table = $('#datatable1').DataTable();
    table.ajax.reload(fnInitComplete);
}

function update2() {
    var table = $('#datatable2').DataTable();
    table.ajax.reload();
}

function add() {
    var course_list = '';
    var series_id = '{{ id }}';
    var $row;
    var data;
    var t = $('#datatable2').DataTable();

    $("#notice_body2 input[type=checkbox]:checked").each(function () {
        $(this).prop('checked', false);
        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        course_list += data.id + "$";
    });
    $.post("/manage/series_course_list_db/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        series_id: series_id,
        course_list: course_list,
        method: 'add',
    }).done(function (data) {
        update1();
        update2();
    }).fail(function (error) {
    });
}

function Del() {

    var $row;
    var data;
    var t = $('#datatable1').DataTable();
    var org_code = '';
    var course_code = '';

    $("#notice_body1 input[type=checkbox]:checked").each(function () {
        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        course_code += data.display_number_with_default + "$";
        org_code += data.org + "$";
    });

    $.post("/manage/series_course_list_db/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        series_id: '{{ id }}',
        course_code: course_code,
        org_code: org_code,
        method: 'delete',
    }).done(function (data) {
        update1();
        update2();
    }).fail(function (error) {
        alert(error);
    });
}


function Update() {
    var org_code = '';
    var course_code = '';
    var course_name = '';
    $("#notice_body1 input[type=checkbox]:checked").each(function () {
        var t = $('#datatable1').DataTable();
        $(this).prop('checked', false);
        var $row = $(this).closest('tr');
        var data = t.row($row.get(0)).data();
        var course = $(this).parent().parent().find("input[type='text']").val();
        org_code += data.org + "$";
        course_code += data.display_number_with_default + "$";
        course_name += course +"$";
    });

        try {
            $.post("/manage/series_course_list_db/", {
                csrfmiddlewaretoken: $.cookie('csrftoken'),
                user_id: '{{ user.id }}',
                series_id: '{{ id }}',
                org_code: org_code,
                course_code: course_code,
                course_name: course_name,
                method: 'update',
            }).done(function (data) {
                update1();
            }).fail(function (error) {
                alert(error);
            });
        } catch (e) {
            alert(e);
        }


}
