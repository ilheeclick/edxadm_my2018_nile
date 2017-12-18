jQuery.ajaxSettings.traditional = true;
$(document).ready(function () {
    setDataTable1();
});

function setDataTable1() {
    var $table = $('#datatable1');

    $table.dataTable({
        dom: '<"toolbar"><"search">rt<"bottom"ip><"clear">',
        "autoWidth": false,
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
            url: "/manage/series_list",
            type: "GET",
            dataType: "json",
            data: buildSearchData1,
            dataSrc: function (json) {
                return json.data;
            }
        },
        columns: [
            {data: "rn"},
            {data: "series_id"},
            {data: "series_name"},
            {data: "cnt"},
            {data: "video_time"},
            {data: "learning_time"},
            {data: "series_seq"},
            {data: "series_seq"},

        ],
        columnDefs: [
            {
                targets: 6, visible: true, name: "pk", render: function (data) {
                return '<a href="/manage/series_complete_list_view/' + data + '"><input type="button" value="보  기" class="btn btn-default"></a>';
            },
            },
            {
                targets: 7, visible: true, name: "pk", render: function (data) {
                return '<a href="/manage/series_course_list_view/' + data + '"><input type="button" value="관  리" class="btn btn-default"></a>';
            },
            },
        ],
        rowsGroup: [
            0,
            5
        ],
        paginate: false,
        "info": false,
        initComplete: function () {
        }


    });

    $table.on('click', 'tr', function () {
        var $row;
        var data;
        var t = $('#datatable1').DataTable();
        $row = $(this).closest('tr');
        data = t.row($row.get(0)).data();
        location.href = '/manage/modi_series/' + data.series_seq
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


function update1() {
    var table = $('#datatable1').DataTable();
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
    $.post("/manage/multisite_course/", {
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
    $.post("/manage/multisite_course/", {
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

    $.post("/manage/multisite_course/", {
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