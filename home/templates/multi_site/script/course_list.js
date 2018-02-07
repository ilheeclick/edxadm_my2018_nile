jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    setDataTable1();
    setDataTable2();

    $.ajax({
        url: '/multisite_org/',
        data: {
            method: 'org'
        }
    }).done(function (data) {
        var html = "<option value='None'>선택하세요.</option>";
        for (var i = 0; i < data.length; i++) {
            //alert(data[key]);
            html += "<option value=" + data[i][0] + ">" + data[i][1] + "</option>"
        }
        $('#org1').html(html);
        $('#org2').html(html);
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
        "scrollY": "300px",
        "scrollCollapse": true,
        ajax: {
            url: "/course_list_db",
            type: "GET",
            dataType: "json",
            data: buildSearchData1,
            dataSrc: function (json) {
                return json.data;
            }
        },
        columns: [
            {data: "pk", name: "pk"},
            {data: "id", name: "id"},
            {data: "rn"},
            {data: "detail_name"},
            {data: "display_name", class: "course_name"},
            {data: "start"},
            {data: "end"},
            {data: "org"},
            {data: "course"},
            {data: "run"},
        ],
        columnDefs: [
            {
                targets: 0, visible: true, name: "pk", render: function (data, type) {
                return '<input type="checkbox" name="' + data + '" value="' + data + '">';
            },
            },
            {
                targets: 1, visible: false,
            },
            {targets: 3, render: function(data) {return '<div style ="width:110px">'+data+'</div>'}},
            {targets: 4, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 5, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 6, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 7, render: function(data) {return '<div style ="width:110px">'+data+'</div>'}},
        ],
        rowsGroup: [
            0,
            5
        ],
        paginate: false,
        "info": false,
        initComplete: function () {
            $('input[type="search"]').attr('class', 'form-control col-sm-10');
            $('input[type="search"]').css("float", "right");
        }
    })
    ;
    $('#search_input1').on('keyup', function () {
        $table.api()
            .search(this.value)
            .draw();
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
        "scrollY": "300px",
        "scrollCollapse": true,
        ajax: {
            url: "/select_list_db",
            type: "GET",
            dataType: "json",
            data: buildSearchData2,
            dataSrc: function (json) {
                return json.data;
            }
        },
        columns: [
            {data: "pk", name: "pk"},
            {data: "id", name: "id"},
            {data: "rn"},
            {data: "detail_name"},
            {data: "display_name", class: "course_name"},
            {data: "start"},
            {data: "end"},
            {data: "org"},
            {data: "course"},
            {data: "run"},
        ],
        columnDefs: [
            {
                targets: 0, visible: true, name: "pk", render: function (data, type) {
                return '<input type="checkbox" name="' + data + '" value="' + data + '">';
            },
            },
            {
                targets: 1, visible: false,
            },
            {targets: 3, render: function(data) {return '<div style ="width:110px">'+data+'</div>'}},
            {targets: 4, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 5, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 6, render: function(data) {return '<div style ="width:200px">'+data+'</div>'}},
            {targets: 7, render: function(data) {return '<div style ="width:110px">'+data+'</div>'}},
        ],
        rowsGroup: [
            0,
            5
        ],
        paginate: false,
        "info": false,
        initComplete: function () {
            $('input[type="search"]').attr('class', 'form-control col-sm-10');
            $('input[type="search"]').css("float", "right");
        }
    })
    ;
    $('#search_input2').on('keyup', function () {
        $table.api()
            .search(this.value)
            .draw();
    });

}


function buildSearchData1() {
    var id = '{{id}}';
    var org = $('#org1').val();
    var obj = {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        id: id,
        site_id: '{{ site_id }}',
        org: org,
    }
    return obj
}

function buildSearchData2() {
    var org = $('#org2').val();
    var obj = {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        site_id: '{{ site_id }}',
        user_id: '{{ user_id }}',
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
    table.ajax.reload();
}

function update2() {
    var table = $('#datatable2').DataTable();
    table.ajax.reload();
}
function Save() {
    var $row;
    var data;
    var t = $('#datatable1').DataTable();
    var course_list = '';
    $("#notice_body1 input[type=checkbox]:checked").each(function () {
        $(this).prop('checked', false);
        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        course_list += data.id + "$";
        console.log($(this).closest('tr'))
        $(this).closest('tr').hide();
    });
    $.post("/multisite_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        site_id: '{{ site_id }}',
        course_list: course_list,
        method: 'add',
    }).done(function (data) {
        update2();
    }).fail(function (error) {
        swal("경고", "이미 추가된 강좌가 존재합니다.", "warning");
    });

}

function Del() {

    var $row;
    var data;
    var t = $('#datatable2').DataTable();
    var course_list = '';
    $("#notice_body2 input[type=checkbox]:checked").each(function () {

        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        course_list += data.id + "$";
    });
    $.post("/multisite_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        site_id: '{{ site_id }}',
        course_list: course_list,
        method: 'delete',
    }).done(function (data) {
        update1();
        update2();
    }).fail(function (error) {
        alert(error);
    });

}
jQuery.fn.center = function () {
    this.css("position", "absolute");
    this.css("top", Math.max(0, (($(window).height() - $(this).outerHeight()) / 2) + $(window).scrollTop()) + "px");
    this.css("left", Math.max(0, (($(window).width() - $(this).outerWidth()) / 2) + $(window).scrollLeft()) + "px");
    return this;
}
function Hide(index) {
    if (index == 'hide') {
        $('#batch_input').css("display", "none");
        $('#input_course').val('');
    }
}
function batch_input() {
    $('#batch_input').center();
    $('#batch_input').css("display", "");
}
function input_Save() {
    var course_list = $('#input_course').val();

    $.post("/multisite_course/", {
        csrfmiddlewaretoken: $.cookie('csrftoken'),
        user_id: '{{ user.id }}',
        site_id: '{{ site_id }}',
        course_list: course_list,
        method: 'input_add',
    }).done(function (data) {
        $('#batch_input').css("display", "none");
        $('#input_course').val('');
        update2();
    }).fail(function (error) {
        swal("경고", "이미 추가된 강좌가 존재합니다.", "warning");
    });
}